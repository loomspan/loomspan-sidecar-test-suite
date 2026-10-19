"""Secret-free exact observation schemas shared by host and container oracles."""


def observations(recipe, variant, action):
    if action != "scenario":
        return {"passed": True}
    if variant == "positive":
        return {
            "formLoginCsrf": True,
            "forwardedIdentity": True,
            "credentialEqual": True,
            "exactRoles": True,
            "methodDenied": True,
            "recordDenied": True,
            "acceptedTransportJwtStatus": 401,
            "successfulCallbackEffects": 1,
        }
    if variant.endswith("loss"):
        return {
            "attempts": 1,
            "forwards": 1,
            "receiverEffects": 1,
            "postEffectResponseLost": True,
            "quietSeconds": 5,
            "acceptanceUnknown": recipe == "standard" and variant == "submission-loss",
            "proxyHttpFailure": recipe == "hardened" and variant == "submission-loss",
            "callbackFailed": variant == "callback-loss",
        }
    return {
        "actualCallerRejected": True,
        "receiverEffects": 0,
        "liveListenerVerified": True,
        "tlsFailureClassified": True,
    }
