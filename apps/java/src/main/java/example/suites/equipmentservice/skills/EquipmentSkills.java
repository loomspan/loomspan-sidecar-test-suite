package example.suites.equipmentservice.skills;
import ai.loomspan.api.*;
import jakarta.annotation.security.RolesAllowed;
import java.util.Map;
import org.springframework.stereotype.Service;
import example.suites.equipmentservice.business.Business;
import example.suites.equipmentservice.business.Business.*;
@Service
public class EquipmentSkills {
    private final Business business;
    public EquipmentSkills(Business business) { this.business = business; }
    @SkillMethod(description = "Retrieve registered asset identity, site access and approval-routing facts; directory facts never grant caller permissions.")
    @RolesAllowed("ASSESS_EQUIPMENT")
    public Map<String, Object> assetContext(
            @SkillParam(description = "Case correlation identifier supplied by the caller.") String caseId,
            @SkillParam(description = "Registered asset identifier; does not grant caller authority.") String assetId) {
        return business.assetContext(caseId, assetId);
    }

    @SkillMethod(description = "Retrieve versioned work orders, recurrence and maintenance observations.")
    @RolesAllowed("ASSESS_EQUIPMENT")
    public Map<String, Object> serviceHistory(
            @SkillParam(description = "Case correlation identifier supplied by the caller.") String caseId,
            @SkillParam(description = "Registered asset identifier; does not grant caller authority.") String assetId) {
        return business.serviceHistory(caseId, assetId);
    }

    @SkillMethod(description = "Retrieve applicable manufacturer manual and bulletin passages.")
    @RolesAllowed("ASSESS_EQUIPMENT")
    public Map<String, Object> referenceEvidence(
            @SkillParam(description = "Case correlation identifier supplied by the caller.") String caseId,
            @SkillParam(description = "Registered asset identifier; does not grant caller authority.") String assetId) {
        return business.referenceEvidence(caseId, assetId);
    }

    @SkillMethod(description = "Retrieve warranty certificate, service agreement and rates.")
    @RolesAllowed("ASSESS_EQUIPMENT")
    public Map<String, Object> serviceTerms(
            @SkillParam(description = "Case correlation identifier supplied by the caller.") String caseId,
            @SkillParam(description = "Registered asset identifier; does not grant caller authority.") String assetId) {
        return business.serviceTerms(caseId, assetId);
    }

    @SkillMethod(description = "Check compatible parts and qualified attendance offers, without reservation.")
    @RolesAllowed("ASSESS_EQUIPMENT")
    public Map<String, Object> serviceResources(
            @SkillParam(description = "Case correlation identifier supplied by the caller.") String caseId,
            @SkillParam(description = "Registered asset identifier; does not grant caller authority.") String assetId) {
        return business.serviceResources(caseId, assetId);
    }

    @SkillMethod(description = "Check compatible loaner and replacement offers, without commitment.")
    @RolesAllowed("ASSESS_EQUIPMENT")
    public Map<String, Object> continuityOptions(
            @SkillParam(description = "Case correlation identifier supplied by the caller.") String caseId,
            @SkillParam(description = "Registered asset identifier; does not grant caller authority.") String assetId) {
        return business.continuityOptions(caseId, assetId);
    }

    @SkillMethod(description = "Evaluate date eligibility and documented findings; model hypotheses are not findings.")
    @RolesAllowed("ASSESS_EQUIPMENT")
    public Map<String, Object> entitlements(
            @SkillParam(description = "Case correlation identifier supplied by the caller.") String caseId,
            @SkillParam(description = "Registered asset identifier; does not grant caller authority.") String assetId) {
        return business.entitlements(caseId, assetId);
    }

    @SkillMethod(description = "Calculate authoritative conditional amounts for checked service strategies.")
    @RolesAllowed("ASSESS_EQUIPMENT")
    public Map<String, Object> quoteOptions(
            @SkillParam(description = "Case correlation identifier supplied by the caller.") String caseId,
            @SkillParam(description = "Registered asset identifier; does not grant caller authority.") String assetId)
            throws Exception {
        return business.quoteOptions(caseId, assetId);
    }

    @SkillMethod(description = "Deterministically record explicit authorized approval and a pending-dispatch request. Requires immutable assessment and matching quote.")
    @RolesAllowed("REQUEST_SERVICE")
    public synchronized Map<String, Object> createServiceRequest(
            @SkillParam(description = "Explicit caller approval bound to an immutable assessment and issued quote; cap is integer USD cents. Authority is verified independently.") Approval approval)
            throws Exception {
        return business.createServiceRequest(approval);
    }
}
