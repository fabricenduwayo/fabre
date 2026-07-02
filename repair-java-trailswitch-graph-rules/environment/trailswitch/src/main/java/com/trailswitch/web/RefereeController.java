package com.trailswitch.web;

import com.trailswitch.service.PathPlanner;
import java.util.List;
import java.util.Map;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.PostMapping;
import org.springframework.web.bind.annotation.RequestBody;
import org.springframework.web.bind.annotation.RestController;

@RestController
public class RefereeController {
    private final PathPlanner planner;

    public RefereeController(PathPlanner planner) {
        this.planner = planner;
    }

    @GetMapping("/health")
    public Map<String, String> health() {
        return Map.of("status", "ok");
    }

    @PostMapping("/v1/plan")
    public Map<String, Object> plan(@RequestBody PlanRequest request) {
        PathPlanner.PlanResult result =
                planner.plan(request.from(), request.to(), request.switches());
        return Map.of(
                "reachable", result.reachable(),
                "path", result.path(),
                "cycle_guard", result.cycleGuard());
    }

    public record PlanRequest(String from, String to, Map<String, String> switches) {}
}
