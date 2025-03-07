package sunnah.api;

import com.intuit.karate.junit5.Karate;

class SetupVerificationRunner {
    
    @Karate.Test
    Karate testSetupVerification() {
        return Karate.run("classpath:sunnah/api/setup-verification.feature");
    }
}
