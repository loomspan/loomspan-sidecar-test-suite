package example.suites.equipmentservice.api;
import example.suites.equipmentservice.business.Business;
import example.infrastructure.execution.ExecutionApi;
import ai.loomspan.api.SkillTemplate;
import java.util.*;
import java.util.concurrent.*;
import org.springframework.boot.SpringApplication;
import org.springframework.boot.autoconfigure.SpringBootApplication;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.context.annotation.Bean;
import org.springframework.http.HttpStatus;
import org.springframework.security.config.annotation.method.configuration.EnableMethodSecurity;
import org.springframework.security.config.annotation.web.builders.HttpSecurity;
import org.springframework.security.core.context.SecurityContextHolder;
import org.springframework.security.oauth2.core.*;
import org.springframework.security.oauth2.jwt.*;
import org.springframework.security.oauth2.server.resource.authentication.*;
import org.springframework.security.web.SecurityFilterChain;
import org.springframework.web.bind.annotation.*;
import org.springframework.web.server.ResponseStatusException;

@RestController
@RequestMapping({"", "/suites/equipment-service"})
public class EquipmentApi {
    private final Business business;
    private final ExecutionApi executions;
    public EquipmentApi(Business business, ExecutionApi executions) {
        this.business = business;
        this.executions = executions;
    }
    @PostMapping("/assessments")
    @ResponseStatus(HttpStatus.ACCEPTED)
    Map<String, Object> assess(@RequestBody Map<String, Object> input) {
        business.scoped((String) input.get("assetId"));
        return executions.submit("resolveEquipment", input);
    }

    @GetMapping("/assessments/{id}")
    Map<String, Object> assessment(@PathVariable String id) {
        return executions.poll(id);
    }

    @PostMapping("/service-requests")
    @ResponseStatus(HttpStatus.ACCEPTED)
    Map<String, Object> commit(@RequestBody Map<String, Object> approval) {
        return executions.submit("createServiceRequest", Map.of("approval", approval));
    }

    @GetMapping("/service-requests/by-key/{key}")
    Map<String, Object> recover(@PathVariable String key) throws Exception {
        return business.recover(key);
    }
}

