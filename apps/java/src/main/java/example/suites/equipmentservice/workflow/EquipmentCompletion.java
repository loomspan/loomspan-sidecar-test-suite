package example.suites.equipmentservice.workflow;
import example.infrastructure.execution.CompletionHandler;
import example.suites.equipmentservice.business.Business;
import java.util.Map;
import org.springframework.stereotype.Component;
@Component
public class EquipmentCompletion implements CompletionHandler {
    private final Business business;
    public EquipmentCompletion(Business business) { this.business = business; }
    public boolean supports(String skill) {
        return skill.equals("resolveEquipment") || skill.equals("createServiceRequest");
    }
    public void complete(String skill, String id, String result, Map<String, Object> state) throws Exception {
        if (skill.equals("resolveEquipment")) state.put("assessmentVersion", business.saveAssessment(id, result));
        if (skill.equals("createServiceRequest") && !"PENDING_DISPATCH".equals(business.read(result).get("status")))
            throw new IllegalStateException("Creation did not return a durable receipt");
    }
}
