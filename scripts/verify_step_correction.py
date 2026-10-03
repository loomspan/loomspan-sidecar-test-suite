"""Offline forensic check of installed Framework bytes; no provider calls."""
import hashlib, json, pathlib, subprocess, zipfile
ROOT = pathlib.Path(__file__).resolve().parents[1]
OUT = ROOT / 'evidence/step-correction-verification-20261002'
LIB = ROOT / '.build/step-correction-verification-libs'
LIB.mkdir(parents=True, exist_ok=True)
installed = pathlib.Path.home()/'.m2/repository/ai/loomspan/loomspan-spring-boot-starter/1.0.0-beta.8-SNAPSHOT/loomspan-spring-boot-starter-1.0.0-beta.8-SNAPSHOT.jar'
with zipfile.ZipFile(ROOT/'apps/java/target/equipment-java-1.0.jar') as jar:
    for name in jar.namelist():
        if name.startswith('BOOT-INF/lib/') and name.endswith('.jar'):
            (LIB/pathlib.Path(name).name).write_bytes(jar.read(name))
class_checks = {}
with zipfile.ZipFile(installed) as jar:
    for name in ['StepActionCorrection', 'StepLoopMissionExecutionEngine', 'StepPromptBuilder']:
        entry = 'ai/loomspan/internal/runtime/step/'+name+'.class'
        current = (ROOT.parent/'loomspan-framework/target/classes'/entry).read_bytes()
        assert jar.read(entry) == current, name+' installed/source compilation mismatch'
        class_checks[name] = hashlib.sha256(current).hexdigest()
source = OUT/'CheckCorrection.java'
source.write_text('''import java.nio.file.*;
import ai.loomspan.internal.serialization.LoomspanJacksonCodecs;
import tools.jackson.core.JacksonException;
public class CheckCorrection {
 public static void main(String[] args) throws Exception {
  var helper=Class.forName("ai.loomspan.internal.runtime.step.StepActionCorrection");
  var failure=Class.forName("ai.loomspan.internal.runtime.step.StepActionCorrection$Failure");
  var parse=helper.getDeclaredMethod("parsingFailure",JacksonException.class,String.class,String.class);parse.setAccessible(true);
  var evidence=helper.getDeclaredMethod("evidence",String.class,failure);evidence.setAccessible(true);
  for(String file:args){
   String candidate=Files.readString(Path.of(file));
   try{LoomspanJacksonCodecs.defaults().planningJson().readValue(candidate,Class.forName("ai.loomspan.internal.runtime.step.StepAction"));throw new AssertionError("Malformed original accepted");}
   catch(JacksonException error){
    String feedback=(String)evidence.invoke(null,candidate,parse.invoke(null,error,candidate,candidate));
    if(!feedback.contains("Unexpected close marker") || !feedback.contains("omitted") || !feedback.contains(LoomspanJacksonCodecs.defaults().planningJson().writeValueAsString(candidate.substring(candidate.length()-128)).substring(1).replaceFirst(".$", "")) || feedback.length()>16000)throw new AssertionError("Incomplete/unbounded feedback");
    System.out.println(Path.of(file).getFileName()+": REJECTED; exact parser reason and long-response tail retained; feedback chars="+feedback.length());
   }
  }
 }
}''')
original = ROOT/'evidence/json-forensics-20261001-220102'
hashes = json.loads((original/'checksums.json').read_text())
for name in ['initial-original.txt','retry-original.txt','initial-request.json','retry-request.json']:
    assert hashlib.sha256((original/name).read_bytes()).hexdigest() == hashes[name]
result = subprocess.run(['C:/hamdev/jbrsdk21/bin/java.exe','--class-path',str(LIB/'*'),str(source),
                         str(original/'initial-original.txt'),str(original/'retry-original.txt')],capture_output=True,text=True)
(OUT/'captured-correction-check.txt').write_text(result.stdout+result.stderr)
assert result.returncode == 0, result.stderr
(OUT/'installed-source-class-check.json').write_text(json.dumps({'installedSha256':hashlib.sha256(installed.read_bytes()).hexdigest(),'compiledSourceClassesMatchInstalled':class_checks,'originalForensicHashesUnchanged':True,'paidCalls':0},indent=2))
print(result.stdout)

