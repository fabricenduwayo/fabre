package com.example.registry;

import org.junit.jupiter.api.Test;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.boot.test.autoconfigure.web.servlet.AutoConfigureMockMvc;
import org.springframework.boot.test.context.SpringBootTest;
import org.springframework.test.web.servlet.MockMvc;

import static org.springframework.test.web.servlet.request.MockMvcRequestBuilders.get;
import static org.springframework.test.web.servlet.result.MockMvcResultMatchers.content;
import static org.springframework.test.web.servlet.result.MockMvcResultMatchers.jsonPath;
import static org.springframework.test.web.servlet.result.MockMvcResultMatchers.status;
import static org.springframework.http.MediaType.APPLICATION_JSON;

@SpringBootTest
@AutoConfigureMockMvc
class RegistryApiTests {

    @Autowired
    private MockMvc mockMvc;

    @Test
    void healthReportsUp() throws Exception {
        mockMvc.perform(get("/health"))
                .andExpect(status().isOk())
                .andExpect(content().contentTypeCompatibleWith(APPLICATION_JSON))
                .andExpect(jsonPath("$.status").value("UP"));
    }

    @Test
    void candidatesReturnsAllSixModels() throws Exception {
        mockMvc.perform(get("/models/candidates"))
                .andExpect(status().isOk())
                .andExpect(content().contentTypeCompatibleWith(APPLICATION_JSON))
                .andExpect(jsonPath("$").isArray())
                .andExpect(jsonPath("$.length()").value(6))
                .andExpect(jsonPath("$[0].id").value("alpha"))
                .andExpect(jsonPath("$[1].id").value("beta"))
                .andExpect(jsonPath("$[2].id").value("gamma"))
                .andExpect(jsonPath("$[3].id").value("delta"))
                .andExpect(jsonPath("$[4].id").value("omega"))
                .andExpect(jsonPath("$[5].id").value("epsilon"));
    }

    @Test
    void candidatesCarryRegistryMetadataFaithfully() throws Exception {
        mockMvc.perform(get("/models/candidates"))
                .andExpect(status().isOk())
                .andExpect(jsonPath("$[0].name").value("churn-model-alpha"))
                .andExpect(jsonPath("$[0].version").value("1.2.0"))
                .andExpect(jsonPath("$[0].metrics.auc").value(0.91))
                .andExpect(jsonPath("$[0].metrics.accuracy").value(0.82))
                .andExpect(jsonPath("$[0].featureHash").value("fh_alpha_9c1"))
                .andExpect(jsonPath("$[1].metrics.auc").value(0.94))
                .andExpect(jsonPath("$[1].metrics.accuracy").value(0.86))
                .andExpect(jsonPath("$[3].featureHash").value("fh_delta_9f4"))
                .andExpect(jsonPath("$[4].metrics.auc").value(0.84))
                .andExpect(jsonPath("$[5].id").value("epsilon"));
    }

    @Test
    void knownModelReturnsItsObject() throws Exception {
        mockMvc.perform(get("/models/gamma"))
                .andExpect(status().isOk())
                .andExpect(content().contentTypeCompatibleWith(APPLICATION_JSON))
                .andExpect(jsonPath("$.id").value("gamma"))
                .andExpect(jsonPath("$.name").value("churn-model-gamma"))
                .andExpect(jsonPath("$.version").value("2.0.0"))
                .andExpect(jsonPath("$.metrics.auc").value(0.88))
                .andExpect(jsonPath("$.featureHash").value("fh_gamma_7d2"));
    }

    @Test
    void unknownModelReturnsNotFound() throws Exception {
        mockMvc.perform(get("/models/does-not-exist"))
                .andExpect(status().isNotFound());
    }

    @Test
    void aliasesReturnsDeploymentMapping() throws Exception {
        mockMvc.perform(get("/aliases"))
                .andExpect(status().isOk())
                .andExpect(content().contentTypeCompatibleWith(APPLICATION_JSON))
                .andExpect(jsonPath("$.production").value("beta"))
                .andExpect(jsonPath("$.canary").value("gamma"))
                .andExpect(jsonPath("$.staging").value("delta"))
                .andExpect(jsonPath("$.previous").value("alpha"));
    }
}
