import java.nio.file.*;
import java.util.*;
import ai.loomspan.api.SkillMethod;
import ai.loomspan.internal.serialization.LoomspanJacksonCodecs;
import ai.loomspan.internal.serialization.LoomspanMethodInputSchemaGenerator;
import example.equipment.Business;

/** Test-only reflection oracle; not an application use of Framework internals. */
class InputContractCheck {
    public static void main(String[] args) throws Exception {
        var mapper=LoomspanJacksonCodecs.defaults().applicationConversion();
        var generator=new LoomspanMethodInputSchemaGenerator(mapper);
        var schemas=new TreeMap<String,Object>();
        for (var method:Business.class.getDeclaredMethods()) {
            if (method.isAnnotationPresent(SkillMethod.class)) {
                schemas.put(method.getName(),generator.generate(method));
            }
        }
        if (schemas.size()!=9) throw new AssertionError("Expected all nine deterministic skills");
        var approval=mapper.readValue("""
          {"assessmentVersion":"v","option":"standard","quoteId":"q","attendance":"window",
           "scope":{"repairHours":3,"parts":["part"],"onlyIfJustifiedByTechnician":true},
           "cap":12345,"idempotencyKey":"key","approved":true}
          """,Business.Approval.class);
        if (approval.cap()!=12345 || approval.scope().repairHours()!=3)
            throw new AssertionError("Approval conversion changed values");
        Files.writeString(Path.of(args[0]),mapper.writeValueAsString(schemas));
        System.out.println("Reflected nine Java skill schemas; typed approval conversion passed.");
    }
}
