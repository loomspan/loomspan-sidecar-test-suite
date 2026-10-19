package ai.loomspan.sdk.example;

import org.springframework.context.annotation.Bean;
import org.springframework.context.annotation.Configuration;
import org.springframework.security.config.Customizer;
import org.springframework.security.config.annotation.web.builders.HttpSecurity;
import org.springframework.security.core.userdetails.User;
import org.springframework.security.provisioning.InMemoryUserDetailsManager;
import org.springframework.security.web.SecurityFilterChain;

@Configuration
@org.springframework.security.config.annotation.method.configuration.EnableMethodSecurity
public class SecurityConfiguration {
    @Bean InMemoryUserDetailsManager users() {
        return new InMemoryUserDetailsManager(
                User.withUsername("alice").password("{noop}fixture").authorities("ROLE_ORDER_EDITOR").build(),
                User.withUsername("bob").password("{noop}fixture").authorities("ROLE_ORDER_EDITOR").build(),
                User.withUsername("literal").password("{noop}fixture").authorities("ORDER_EDITOR").build());
    }
    @Bean @org.springframework.core.annotation.Order(0)
    SecurityFilterChain security(HttpSecurity http) throws Exception {
        return http.authorizeHttpRequests(auth -> auth.anyRequest().authenticated())
                .formLogin(Customizer.withDefaults()).build();
    }
}
