package example.equipment;

import ai.loomspan.api.*;
import tools.jackson.databind.json.JsonMapper;
import java.util.*;
import java.time.*;
import java.sql.*;
import org.springframework.beans.factory.annotation.Value;
import jakarta.annotation.security.RolesAllowed;
import org.springframework.security.core.context.SecurityContextHolder;
import org.springframework.security.oauth2.server.resource.authentication.JwtAuthenticationToken;
import org.springframework.stereotype.Service;
import org.springframework.web.client.RestClient;

@Service
public class Business {
    private final RestClient fixtures;
    private final String url;
    private final JsonMapper json=JsonMapper.builder().build();
    Business(@Value("${equipment.fixtures}") String fixtures,@Value("${spring.datasource.url}") String url) throws Exception {
        this.fixtures=RestClient.create(fixtures);this.url=url;
        try(var c=db();var s=c.createStatement()){
            s.execute("CREATE TABLE IF NOT EXISTS assessments(version TEXT PRIMARY KEY, owner TEXT, asset TEXT, body TEXT)");
            s.execute("CREATE TABLE IF NOT EXISTS requests(owner TEXT, key TEXT, content TEXT, receipt TEXT, PRIMARY KEY(owner,key))");
            s.execute("CREATE TABLE IF NOT EXISTS quotes(id TEXT PRIMARY KEY, body TEXT)");
        }
    }
    Connection db() throws SQLException {var c=DriverManager.getConnection(url);try(var s=c.createStatement()){s.execute("PRAGMA busy_timeout=30000");}return c;}
    Map<String,Object> read(String text){return json.readValue(text,Map.class);}
    String encode(Object value){return json.writeValueAsString(value);}
    String user(){return SecurityContextHolder.getContext().getAuthentication().getName();}
    String issuer(){return ((JwtAuthenticationToken)SecurityContextHolder.getContext().getAuthentication()).getToken().getIssuer().toString();}
    void scoped(String asset){if(!Set.of("maya","luis").contains(user()) || !Set.of("NB-P240-017","NB-P240-018").contains(asset))throw new org.springframework.security.access.AccessDeniedException("site scope denied");}
    Map<String,Object> record(String caseId,String kind){
        return fixtures.get().uri("/records/{caseId}/{kind}",caseId,kind).retrieve().body(Map.class);
    }
    Map<String,Object> data(String caseId,String kind){return (Map<String,Object>)record(caseId,kind).get("data");}
    Map<String,Object> fetch(String kind,String caseId,String assetId){scoped(assetId);var value=record(caseId,kind);value.put("assetId",assetId);return value;}

    @SkillMethod(description="Retrieve registered asset identity, site access and approval-routing facts; directory facts never grant caller permissions.") @RolesAllowed("ASSESS_EQUIPMENT")
    public Map<String,Object> assetContext(@SkillParam String caseId,@SkillParam String assetId,@SkillParam(required=false) Map<String,Object> context){
        var value=fetch("assetContext",caseId,assetId);
        if(!assetId.equals(((Map<?,?>)value.get("data")).get("assetId")))throw new IllegalArgumentException("Registered asset context unavailable");
        return value;
    }

    @SkillMethod(description="Retrieve versioned work orders, recurrence and maintenance observations.") @RolesAllowed("ASSESS_EQUIPMENT")
    public Map<String,Object> serviceHistory(@SkillParam String caseId,@SkillParam String assetId,@SkillParam(required=false) Map<String,Object> context){return fetch("serviceHistory",caseId,assetId);}
    @SkillMethod(description="Retrieve applicable manufacturer manual and bulletin passages.") @RolesAllowed("ASSESS_EQUIPMENT")
    public Map<String,Object> referenceEvidence(@SkillParam String caseId,@SkillParam String assetId,@SkillParam(required=false) Map<String,Object> context){return fetch("referenceEvidence",caseId,assetId);}
    @SkillMethod(description="Retrieve warranty certificate, service agreement and rates.") @RolesAllowed("ASSESS_EQUIPMENT")
    public Map<String,Object> serviceTerms(@SkillParam String caseId,@SkillParam String assetId,@SkillParam(required=false) Map<String,Object> context){return fetch("serviceTerms",caseId,assetId);}
    @SkillMethod(description="Check compatible parts and qualified attendance offers, without reservation.") @RolesAllowed("ASSESS_EQUIPMENT")
    public Map<String,Object> serviceResources(@SkillParam String caseId,@SkillParam String assetId,@SkillParam(required=false) Map<String,Object> context){return fetch("serviceResources",caseId,assetId);}
    @SkillMethod(description="Check compatible loaner and replacement offers, without commitment.") @RolesAllowed("ASSESS_EQUIPMENT")
    public Map<String,Object> continuityOptions(@SkillParam String caseId,@SkillParam String assetId,@SkillParam(required=false) Map<String,Object> context){return fetch("continuityOptions",caseId,assetId);}
    @SkillMethod(description="Evaluate date eligibility and documented findings; model hypotheses are not findings.") @RolesAllowed("ASSESS_EQUIPMENT")
    public Map<String,Object> entitlements(@SkillParam String caseId,@SkillParam String assetId,@SkillParam(required=false) Map<String,Object> context){
        var result=fetch("entitlements",caseId,assetId);var terms=data(caseId,"serviceTerms");var cert=(Map<String,Object>)terms.get("certificate");
        var now=OffsetDateTime.parse((String)data(caseId,"clock").get("now")).toLocalDate();
        boolean inPeriod=!now.isBefore(LocalDate.parse((String)cert.get("start"))) && now.isBefore(LocalDate.parse((String)cert.get("endExclusive")));
        var findings=(List<Map<String,Object>>)((Map<?,?>)result.get("data")).get("findings");var covered=new ArrayList<String>();
        for(var f:findings)if(inPeriod && Boolean.TRUE.equals(f.get("authorizedTechnician")) && Boolean.TRUE.equals(f.get("confirmedManufacturingDefect")) && !Boolean.TRUE.equals(f.get("disputed")))covered.addAll((List<String>)f.get("items"));
        result.put("determination",Map.of("status",!covered.isEmpty()?"PARTIAL_OR_COVERED":inPeriod?"PENDING":"OUTSIDE_PERIOD","coveredItems",covered,"diagnosisIncluded",true,"travelIncluded",true,"premiumCovered",false));return result;
    }
    @SkillMethod(description="Calculate authoritative conditional amounts for checked service strategies.") @RolesAllowed("ASSESS_EQUIPMENT")
    public Map<String,Object> quoteOptions(@SkillParam String caseId,@SkillParam String assetId,@SkillParam(required=false) Map<String,Object> context) throws Exception {
        scoped(assetId);var terms=data(caseId,"serviceTerms");var resources=data(caseId,"serviceResources");var entitlement=entitlements(caseId,assetId,context);
        var rates=(Map<String,Number>)terms.get("rates");int repair=2*rates.get("repairHourly").intValue()+rates.get("sensor").intValue()+rates.get("connector").intValue();var quotes=new ArrayList<Map<String,Object>>();
        for(String option:List.of("expedited","standard")){
            int premium=option.equals("expedited")?rates.get("expedited").intValue():0;
            var q=new LinkedHashMap<String,Object>();q.put("quoteId",caseId+"-"+option+"-v1");q.put("option",option);q.put("currency","USD");q.put("maxExposure",repair+premium);q.put("fullyCoveredScopeMaximum",premium);q.put("coverage","PENDING");q.put("attendance",((Map<?,?>)resources.get(option)).get("arrival"));q.put("scope",Map.of("repairHours",2,"parts",List.of("S17-B","H17-B"),"onlyIfJustifiedByTechnician",true));q.put("expiresAt",resources.get("expiresAt"));q.put("reservation",false);q.put("restorationGuaranteed",false);quotes.add(q);
            try(var c=db();var s=c.prepareStatement("INSERT OR IGNORE INTO quotes VALUES(?,?)")){s.setString(1,(String)q.get("quoteId"));s.setString(2,encode(q));s.executeUpdate();}
        }
        return Map.of("caseId",caseId,"assetId",assetId,"quotes",quotes,"entitlement",entitlement);
    }
    String saveAssessment(String execution,String result) throws Exception {
        var value=read(result);scoped((String)value.get("assetId"));
        for(String key:List.of("uncertainty","quotes","selectedOption","acceptedRisk","nextDecision","citations","equipmentAssessment"))if(!value.containsKey(key))throw new IllegalArgumentException("Incomplete assessment");
        if(!List.of("expedited","standard","loaner","replacement","defer","undecided").contains(value.get("selectedOption")))throw new IllegalArgumentException("selectedOption must be an option name, not a quote ID");
        var quotes=(List<Map<String,Object>>)value.get("quotes");if(quotes.isEmpty())throw new IllegalArgumentException("Missing quotes");
        var expected=Set.of(value.get("caseId")+"-expedited-v1",value.get("caseId")+"-standard-v1");
        if(quotes.size()!=2 || !new HashSet<>(quotes.stream().map(q->q.get("quoteId")).toList()).equals(expected))throw new IllegalArgumentException("Missing, duplicate or foreign-case quote");
        try(var c=db()){
            for(var q:quotes)try(var s=c.prepareStatement("SELECT body FROM quotes WHERE id=?")){s.setString(1,(String)q.get("quoteId"));try(var r=s.executeQuery()){if(!r.next() || !read(r.getString(1)).equals(q))throw new IllegalArgumentException("Model altered authoritative quote");}}
            try(var s=c.prepareStatement("INSERT OR IGNORE INTO assessments VALUES(?,?,?,?)")){s.setString(1,execution+"-v1");s.setString(2,user());s.setString(3,(String)value.get("assetId"));s.setString(4,result);s.executeUpdate();}
        }return execution+"-v1";
    }
    @SkillMethod(description="Deterministically record explicit authorized approval and a pending-dispatch request. Requires immutable assessment and matching quote.") @RolesAllowed("REQUEST_SERVICE")
    public synchronized Map<String,Object> createServiceRequest(@SkillParam Map<String,Object> approval) throws Exception {
        if(!user().equals("luis"))throw new org.springframework.security.access.AccessDeniedException("No spending grant");
        if(!approval.keySet().containsAll(List.of("assessmentVersion","option","quoteId","attendance","scope","cap","idempotencyKey","approved")) || !Boolean.TRUE.equals(approval.get("approved")))throw new IllegalArgumentException("Explicit complete approval required");
        String owner=issuer()+"|"+user();String key=(String)approval.get("idempotencyKey");
        try(var c=db()){
            c.setAutoCommit(false);
            try{
                try(var s=c.prepareStatement("SELECT content,receipt FROM requests WHERE owner=? AND key=?")){s.setString(1,owner);s.setString(2,key);try(var r=s.executeQuery()){if(r.next()){if(!read(r.getString(1)).equals(approval))throw new IllegalArgumentException("Idempotency content conflict");return read(r.getString(2));}}}
                Map<String,Object> value;
                try(var s=c.prepareStatement("SELECT asset,body FROM assessments WHERE version=?")){s.setString(1,(String)approval.get("assessmentVersion"));try(var r=s.executeQuery()){if(!r.next())throw new IllegalArgumentException("Assessment not found");scoped(r.getString(1));value=read(r.getString(2));}}
                var quote=((List<Map<String,Object>>)value.get("quotes")).stream().filter(q->q.get("quoteId").equals(approval.get("quoteId")) && q.get("option").equals(approval.get("option"))).findFirst().orElseThrow();
                if(!quote.get("scope").equals(approval.get("scope")) || !quote.get("attendance").equals(approval.get("attendance")) || !quote.get("maxExposure").equals(approval.get("cap")) || ((Number)approval.get("cap")).intValue()>100000)throw new IllegalArgumentException("Approved terms differ or exceed ceiling");
                var now=(String)data((String)value.get("caseId"),"clock").get("now");if(!OffsetDateTime.parse(now).isBefore(OffsetDateTime.parse((String)quote.get("expiresAt"))))throw new IllegalArgumentException("Requote required");
                var receipt=Map.<String,Object>of("requestId",UUID.randomUUID().toString(),"status","PENDING_DISPATCH","assetId",value.get("assetId"),"caseId",value.get("caseId"),"approval",approval,"approver",Map.of("issuer",issuer(),"subject",user()),"quote",quote,"evidence",value.get("citations"),"createdAt",now);
                try(var s=c.prepareStatement("INSERT INTO requests VALUES(?,?,?,?)")){s.setString(1,owner);s.setString(2,key);s.setString(3,encode(approval));s.setString(4,encode(receipt));s.executeUpdate();}c.commit();return receipt;
            }catch(Exception e){c.rollback();throw e;}
        }
    }
    @RolesAllowed("REQUEST_SERVICE")
    public Map<String,Object> recover(String key) throws Exception {
        try(var c=db();var s=c.prepareStatement("SELECT receipt FROM requests WHERE owner=? AND key=?")){s.setString(1,issuer()+"|"+user());s.setString(2,key);try(var r=s.executeQuery()){if(!r.next())throw new org.springframework.web.server.ResponseStatusException(org.springframework.http.HttpStatus.NOT_FOUND);return read(r.getString(1));}}
    }
}
