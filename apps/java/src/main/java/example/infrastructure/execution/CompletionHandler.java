package example.infrastructure.execution;
import java.util.Map;
public interface CompletionHandler {
    boolean supports(String skill);
    void complete(String skill, String id, String result, Map<String, Object> state) throws Exception;
}
