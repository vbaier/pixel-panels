package com.grizzhak.pixelpanels.panelservice;

import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.springframework.boot.CommandLineRunner;
import org.springframework.context.annotation.Bean;
import org.springframework.context.annotation.Configuration;

/**
 * Initializes our in-memory database. Note that Spring will inject our PanelRepository here
 * automatically due to a feature where it injects bean dependencies without @Autowired if
 * there is exactly one constructor defined.
 *
 * It should also be noted that our PanelRepository is not explicitly created. Simply defining
 * an interface that extends JpaRepository and having a supported database declared as a
 * dependency in pom.xml will drive Spring's autoconfiguration feature to create the relevant
 * beans for that interface. It is this that actually creates the PanelRepository which is
 * injected. See the <a href="https://docs.spring.io/spring-data/jpa/docs/2.6.2/reference/html/#repositories.create-instances">
 * Spring Data JPA Docs</a> as an initial reference describing this.
 *
 * @author Vincent Baier
 */
@Configuration
class LoadDatabase {

    private static final Logger log = LoggerFactory.getLogger(LoadDatabase.class);

    @Bean
    CommandLineRunner initDatabase(PanelRepository repository) {

//        return args -> {
//            log.info("Preloading " + repository.save(new Panel("./data/Test_64x32.gif")));
//        };
        return args -> {;};
    }
}