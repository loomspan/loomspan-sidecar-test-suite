package example.equipment;

import java.nio.file.*;
import java.util.*;
import org.springframework.security.authentication.UsernamePasswordAuthenticationToken;
import org.springframework.security.core.context.SecurityContextHolder;
import tools.jackson.databind.json.JsonMapper;

/** Local publication guard checks; scripted caller, no authorization or Framework claim. */
public class BusinessOutputCheck {
    public static void main(String[] args) throws Exception {
        var json = JsonMapper.builder().build();
        var document = json.readValue(Files.readString(Path.of(args[0])), Map.class);
        if (!Boolean.FALSE.equals(document.get("approved"))) throw new AssertionError("Diagnostic approved");
        var samples = (Map<String, Map<String, Object>>) document.get("samples");
        SecurityContextHolder.getContext().setAuthentication(
            new UsernamePasswordAuthenticationToken("maya", "offline-placeholder", List.of()));
        int checks = 0;
        try {
            for (String path : List.of("java", "sidecar")) {
                var value = (Map<String, Object>) samples.get(path).get("candidate");
                var app = new Business("http://127.0.0.1:1", "jdbc:sqlite:" + Path.of(args[1], path + ".db"));
                try (var c = app.db()) {
                    for (var quote : (List<Map<String, Object>>) value.get("quotes")) {
                        try (var s = c.prepareStatement("INSERT INTO quotes VALUES(?,?)")) {
                            s.setString(1, (String) quote.get("quoteId"));
                            s.setString(2, json.writeValueAsString(quote)); s.executeUpdate();
                        }
                    }
                }
                var quote = ((List<Map<String, Object>>) value.get("quotes")).getFirst();
                for (String selection : List.of((String) quote.get("quoteId"), "Express", "missing")) {
                    var damaged = new HashMap<>(value);
                    if (selection.equals("missing")) damaged.remove("selectedOption");
                    else damaged.put("selectedOption", selection);
                    try { app.saveAssessment("invalid", json.writeValueAsString(damaged));
                        throw new AssertionError("Invalid selection published");
                    } catch (IllegalArgumentException expected) { checks++; }
                }
                var damaged = json.readValue(json.writeValueAsString(value), Map.class);
                ((Map<String, Object>) ((List<?>) damaged.get("quotes")).getFirst()).put("maxExposure", 780);
                try { app.saveAssessment("scaled", json.writeValueAsString(damaged));
                    throw new AssertionError("Dollar-scaled quote published");
                } catch (IllegalArgumentException expected) { checks++; }
                try (var c = app.db(); var s = c.createStatement()) {
                    try (var r = s.executeQuery("SELECT COUNT(*) FROM assessments")) {
                        if (!r.next() || r.getInt(1) != 0) throw new AssertionError("Invalid assessment persisted");
                    }
                    try (var r = s.executeQuery("SELECT COUNT(*) FROM requests")) {
                        if (!r.next() || r.getInt(1) != 0) throw new AssertionError("Commitment created");
                    }
                }
                app.saveAssessment("local-positive", json.writeValueAsString(value));
                checks++;
            }
        } finally { SecurityContextHolder.clearContext(); }
        System.out.println(checks + " Java offline publication checks passed; temporary databases only; no model/Framework or semantic acceptance.");
    }
}
