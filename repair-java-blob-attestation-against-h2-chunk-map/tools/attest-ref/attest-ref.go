// Reference attestor. Reads a blob store and writes the correct attestation
// report. It is the ground truth the agent's control must agree with; shipped as
// a native binary so its decision rules cannot be read off the bytecode.
//
// H2 is Java-native, so the store's rows are exported with the H2 tool's CSVWRITE
// and read back here; the verdict rules run in this binary.
package main

import (
	"crypto/sha256"
	"encoding/csv"
	"encoding/json"
	"fmt"
	"os"
	"os/exec"
	"path/filepath"
	"sort"
	"strconv"
	"strings"
)

type object struct {
	id       string
	declared string
	algo     string
	blobPath string
	size     int64
}

type reasoned struct {
	ObjectID string `json:"object_id"`
	Reason   string `json:"reason"`
}

type conflict struct {
	ObjectID     string `json:"object_id"`
	CacheStatus  string `json:"cache_status"`
	ActualStatus string `json:"actual_status"`
}

type report struct {
	Intact       []string   `json:"intact"`
	Corrupt      []reasoned `json:"corrupt"`
	Unattestable []reasoned `json:"unattestable"`
	Conflicts    []conflict `json:"conflicts"`
}

func main() {
	jdbcURL := "jdbc:h2:file:/app/store/objects"
	out := "/app/build/attestation-report.json"
	if len(os.Args) > 1 {
		jdbcURL = os.Args[1]
	}
	if len(os.Args) > 2 {
		out = os.Args[2]
	}
	if err := run(jdbcURL, out); err != nil {
		fmt.Fprintln(os.Stderr, "attest-ref:", err)
		os.Exit(1)
	}
}

func run(jdbcURL, out string) error {
	root := storeRoot(jdbcURL)
	objects, err := loadObjects(jdbcURL)
	if err != nil {
		return err
	}
	chunks, err := loadChunks(jdbcURL)
	if err != nil {
		return err
	}
	cache, err := loadCache(jdbcURL)
	if err != nil {
		return err
	}

	rep := report{Intact: []string{}, Corrupt: []reasoned{}, Unattestable: []reasoned{}, Conflicts: []conflict{}}
	ids := make([]string, 0, len(objects))
	for id := range objects {
		ids = append(ids, id)
	}
	sort.Strings(ids)

	for _, id := range ids {
		obj := objects[id]
		status, reason := attest(root, obj, chunks[id])
		switch status {
		case "intact":
			rep.Intact = append(rep.Intact, id)
		case "corrupt":
			rep.Corrupt = append(rep.Corrupt, reasoned{id, reason})
		default:
			rep.Unattestable = append(rep.Unattestable, reasoned{id, reason})
		}
		if c, ok := cache[id]; ok && conflicts(c, status) {
			rep.Conflicts = append(rep.Conflicts, conflict{id, c, status})
		}
	}

	body, err := json.MarshalIndent(rep, "", "  ")
	if err != nil {
		return err
	}
	if dir := filepath.Dir(out); dir != "" {
		os.MkdirAll(dir, 0o755)
	}
	return os.WriteFile(out, body, 0o644)
}

// attest judges the object against its declaration. The current chunk map is the
// latest generation's rows in ordinal order; either that or the blob counts as a
// surviving copy when it reads back at the declared length; only sha256 is
// accepted.
func attest(root string, obj object, rows []chunkRow) (string, string) {
	var surviving [][]byte
	if c := chunkCopy(root, rows); c != nil && int64(len(c)) == obj.size {
		surviving = append(surviving, c)
	}
	if b := blobCopy(root, obj.blobPath); b != nil && int64(len(b)) == obj.size {
		surviving = append(surviving, b)
	}
	if len(surviving) == 0 {
		return "unattestable", "missing_content"
	}
	if !strings.EqualFold(obj.algo, "sha256") {
		return "unattestable", "unsupported_digest"
	}
	for _, copy := range surviving {
		sum := sha256.Sum256(copy)
		if strings.EqualFold(hex(sum[:]), obj.declared) {
			return "intact", ""
		}
	}
	return "corrupt", "digest_mismatch"
}

func chunkCopy(root string, rows []chunkRow) []byte {
	if len(rows) == 0 {
		return nil
	}
	latest := rows[0].generation
	for _, r := range rows {
		if r.generation > latest {
			latest = r.generation
		}
	}
	current := make([]chunkRow, 0, len(rows))
	for _, r := range rows {
		if r.generation == latest {
			current = append(current, r)
		}
	}
	sort.Slice(current, func(i, j int) bool { return current[i].ordinal < current[j].ordinal })
	var buf []byte
	for _, r := range current {
		data, err := os.ReadFile(filepath.Join(root, r.path))
		if err != nil {
			return nil
		}
		buf = append(buf, data...)
	}
	return buf
}

func blobCopy(root, blobPath string) []byte {
	if blobPath == "" {
		return nil
	}
	data, err := os.ReadFile(filepath.Join(root, blobPath))
	if err != nil {
		return nil
	}
	return data
}

func conflicts(cacheStatus, actual string) bool {
	if cacheStatus == "verified" {
		return actual != "intact"
	}
	if cacheStatus == "failed" {
		return actual != "corrupt"
	}
	return false
}

type chunkRow struct {
	generation int
	ordinal    int
	path       string
}

func loadObjects(jdbcURL string) (map[string]object, error) {
	rows, err := query(jdbcURL,
		"SELECT object_id, declared_digest, digest_algo, blob_path, size_bytes FROM objects")
	if err != nil {
		return nil, err
	}
	out := make(map[string]object)
	for _, r := range rows[1:] {
		size, _ := strconv.ParseInt(r[4], 10, 64)
		out[r[0]] = object{id: r[0], declared: r[1], algo: r[2], blobPath: r[3], size: size}
	}
	return out, nil
}

func loadChunks(jdbcURL string) (map[string][]chunkRow, error) {
	rows, err := query(jdbcURL,
		"SELECT object_id, generation, ordinal, chunk_path FROM object_chunks")
	if err != nil {
		return nil, err
	}
	out := make(map[string][]chunkRow)
	for _, r := range rows[1:] {
		gen, _ := strconv.Atoi(r[1])
		ord, _ := strconv.Atoi(r[2])
		out[r[0]] = append(out[r[0]], chunkRow{generation: gen, ordinal: ord, path: r[3]})
	}
	return out, nil
}

func loadCache(jdbcURL string) (map[string]string, error) {
	rows, err := query(jdbcURL, "SELECT object_id, status FROM attestation_cache")
	if err != nil {
		return nil, err
	}
	out := make(map[string]string)
	for _, r := range rows[1:] {
		out[r[0]] = r[1]
	}
	return out, nil
}

// query exports a SELECT to CSV with the H2 tool and returns the parsed rows,
// header included.
func query(jdbcURL, sql string) ([][]string, error) {
	tmp, err := os.MkdirTemp("", "attest-ref")
	if err != nil {
		return nil, err
	}
	defer os.RemoveAll(tmp)

	csvPath := filepath.Join(tmp, "out.csv")
	script := filepath.Join(tmp, "q.sql")
	safe := strings.ReplaceAll(sql, "'", "''")
	if err := os.WriteFile(script, []byte(fmt.Sprintf("CALL CSVWRITE('%s', '%s');\n", csvPath, safe)), 0o644); err != nil {
		return nil, err
	}
	readURL := jdbcURL
	if !strings.Contains(readURL, "IFEXISTS") {
		readURL += ";IFEXISTS=TRUE"
	}
	cmd := exec.Command("java", "-cp", h2Jar(), "org.h2.tools.RunScript",
		"-url", readURL, "-user", "sa", "-script", script)
	if outBytes, err := cmd.CombinedOutput(); err != nil {
		return nil, fmt.Errorf("h2 export failed: %v: %s", err, outBytes)
	}
	f, err := os.Open(csvPath)
	if err != nil {
		return nil, err
	}
	defer f.Close()
	return csv.NewReader(f).ReadAll()
}

func h2Jar() string {
	for _, dir := range []string{"/app/lib", filepath.Join(exeDir(), "..", "lib")} {
		if hits, _ := filepath.Glob(filepath.Join(dir, "h2-*.jar")); len(hits) > 0 {
			return hits[0]
		}
	}
	return "/app/lib/h2-2.2.224.jar"
}

func exeDir() string {
	exe, err := os.Executable()
	if err != nil {
		return "."
	}
	return filepath.Dir(exe)
}

func storeRoot(jdbcURL string) string {
	i := strings.Index(jdbcURL, "file:")
	if i < 0 {
		return "."
	}
	path := jdbcURL[i+len("file:"):]
	if s := strings.IndexByte(path, ';'); s >= 0 {
		path = path[:s]
	}
	return filepath.Dir(path)
}

func hex(b []byte) string {
	const digits = "0123456789abcdef"
	out := make([]byte, len(b)*2)
	for i, v := range b {
		out[i*2] = digits[v>>4]
		out[i*2+1] = digits[v&0xF]
	}
	return string(out)
}
