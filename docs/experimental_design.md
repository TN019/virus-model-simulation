# Experiment Design

## 1. Aim

The aim of this experiment design is to test whether our Python implementation can reproduce the main behaviour of the original NetLogo Virus model, and then use an extended version of the model to investigate the effect of imperfect immunity on virus persistence.

The project contains two experiment stages:

1. Replication experiments, where the same parameter settings are run in both NetLogo and Python.
2. Extension experiments, where a new variable is added to the Python model to study how imperfect immunity changes the behaviour of the virus.

The goal of replication is not to produce exactly identical output values at every tick. Since the Virus model is stochastic, different runs naturally produce different results. Instead, replication is judged by whether the Python implementation produces similar overall patterns, trends, and summary behaviour under the same model conditions.

## 2. Replication Experiment Aim

The aim of the replication experiment is to determine whether the Python implementation can reproduce the major behavioural patterns of the original NetLogo Virus model under the same parameter settings.

The comparison focuses on aggregate model behaviour rather than exact tick-by-tick output. This is because NetLogo and Python may use different random number generation, update order, and implementation details. Therefore, exact numerical equality is not expected.

A successful replication should show that the Python model responds to changes in key parameters in the same general way as the NetLogo model.

## 3. Replication Experiment Design

The replication experiment will use three to five shared parameter settings. Each setting will be run in both the original NetLogo model and the Python implementation.


Each condition will be run 30 times in both NetLogo and Python, using different random seeds. Each run will last 1040 ticks, representing 20 years. Repeated runs are necessary because the model contains random movement, random infection, random recovery or death, and random reproduction.

For each run, the model will record the population state over time. The comparison will then be based on average trends and summary measures across repeated runs.

## 4. Replication Parameter Sets

The replication experiment will use the following parameter settings.

| Condition                 |       Infectiousness |      Chance recover |             Duration | Purpose                  |
| ------------------------- | -------------------: | ------------------: | -------------------: | ------------------------ |
| Baseline                  |     [baseline value] |    [baseline value] |     [baseline value] | Normal model behaviour   |
| Low infectiousness        |  lower than baseline |    same as baseline |     same as baseline | Weaker transmission      |
| High infectiousness       | higher than baseline |    same as baseline |     same as baseline | Stronger transmission    |
| Low recovery chance       |     same as baseline | lower than baseline |     same as baseline | More deadly infection    |
| Longer infection duration |     same as baseline |    same as baseline | higher than baseline | Longer infectious period |


If only four conditions are used, the longer infection duration condition can be removed. The baseline, low infectiousness, high infectiousness, and low recovery chance conditions are the most important because they test different core mechanisms of the model.

## 5. Outputs Recorded for Replication

For each tick, the following outputs will be recorded:

* susceptible population
* infected population
* immune population
* total population
* percentage infected
* percentage immune

For each complete run, the following summary measures will be calculated:

* peak infected percentage
* tick of peak infection
* final infected percentage
* final immune percentage
* final population size
* whether the virus persists at the final tick
* time to extinction, if the infected population reaches zero

Because the model is stochastic, the analysis should also consider the distribution of outcomes across repeated runs, not only the average trend. In particular, the comparison should examine how often the virus persists, how often it dies out, and how much variation exists in peak infection and extinction time under each condition.

These measures allow comparison of both short-term outbreak behaviour and long-term virus survival.

## 6. Replication Comparison Method

The NetLogo and Python models will not be compared by checking whether every tick produces the same value. Instead, the comparison will focus on whether both models show similar behavioural patterns under the same conditions.

The main comparison questions are:

* Does the baseline condition produce a similar outbreak pattern?
* Does lower infectiousness reduce the outbreak in both models?
* Does higher infectiousness increase the outbreak in both models?
* Does lower recovery chance increase deaths or reduce population size in both models?
* Does longer infection duration make the virus more persistent in both models?

The Python implementation will be considered a successful replication if it produces the same direction of change and broadly similar trends across the shared parameter settings. This judgement should be based on both average behaviour and the distribution of repeated-run outcomes.

## 7. Extension Aim

The aim of the extension experiment is to investigate how imperfect immunity affects the long-term persistence and outbreak dynamics of the virus.

In the original model, recovered individuals become immune and cannot be infected again until their immunity expires. This means immunity is temporary but fully protective.

The extension changes this assumption by allowing immune individuals to be reinfected with a small probability after contact with an infectious individual. This allows the model to test whether less reliable immunity makes the virus more likely to survive in the population over time.

## 8. Extension Research Question

Does increasing the probability of reinfection among immune individuals increase the likelihood that the virus persists in the population?

## 9. Extension Design

The extension introduces a new variable called immune reinfection probability.

This variable controls the probability that an immune individual becomes infected again after contact with an infectious individual.

In the baseline model, immune individuals are fully protected until their immunity expires. In the extended model, immune individuals still have protection, but the protection is not perfect. When an immune individual shares a location with an infectious individual, there is a small chance that the immune individual becomes infectious again.

This adds a new possible transition from immune to infectious.

This reinfection rule should be treated as a distinct infection mechanism for immune individuals, rather than exactly the same rule used for susceptible individuals. If reinfection occurs, the individual transitions directly from immune to infectious before immunity expires.

The original immunity expiry rule is still retained. Therefore, immune individuals may return to the susceptible state when their immunity duration ends, or they may become infectious earlier if reinfection occurs.

## 10. Extension Parameter Values

The extension experiment will vary the immune reinfection probability while keeping the other model parameters fixed.

| Condition                 | Immune reinfection probability | Purpose                                                                           |
| ------------------------- | -----------------------------: | --------------------------------------------------------------------------------- |
| Secure immunity           |                           0.00 | Represents the original assumption where immune individuals cannot be reinfected. |
| Low imperfect immunity    |                           0.02 | Tests a small chance of reinfection.                                              |
| Medium imperfect immunity |                           0.05 | Tests a moderate chance of reinfection.                                           |
| High imperfect immunity   |                           0.10 | Tests a stronger imperfect immunity effect.                                       |

Each extension condition will be run 30 times in the extended Python model, using different random seeds. Each run will last 1040 ticks, representing 20 years. The original NetLogo model is not used for this experiment because immune reinfection is the new behaviour added in our Python extension.

The immune reinfection probability is represented as a value between 0 and 1, where 0.05 means a 5% chance of reinfection after contact with an infectious individual.

Although the parameter is represented on a 0 to 1 scale, the experiment only tests values up to 0.10 because reinfection is evaluated at each infectious contact. A value of 0.10 already represents a relatively strong chance of immune failure per contact, while still preserving the idea that immunity provides partial protection.

## 11. Expected Extension Behaviour

The expected behaviour is that higher immune reinfection probability will make the virus more likely to persist in the population.

In the original model, immune individuals are temporarily removed from the pool of possible hosts. This can make it harder for the virus to survive after the initial outbreak, especially if many people become immune at the same time.

In the extended model, immune individuals are no longer completely protected. This means the virus may still have access to potential hosts even when the susceptible population is low. As a result, the virus may survive for longer, have a higher final infected percentage, or show a higher persistence rate.

However, the effect may not be purely linear. If reinfection becomes too common, the model may also show larger outbreaks, increased deaths, or changes in population size. Therefore, the extension experiment will consider both virus persistence and population-level effects.

## 12. Extension Outputs

The extension experiment will record the same basic outputs as the replication experiment:

* susceptible population
* infected population
* immune population
* total population
* percentage infected
* percentage immune

The main summary measures for the extension are:

* persistence rate at the final tick
* final infected percentage
* peak infected percentage
* time to extinction
* final population size

Because the extension is also stochastic, the results should also compare the distribution of outcomes across runs. This includes how often persistence occurs, how often extinction occurs, and how much variation exists in peak infection and extinction time at different reinfection levels.

These outputs are used to determine whether imperfect immunity mainly affects the initial outbreak, long-term virus survival, or the overall population dynamics.

## 13. Extension Hypothesis

The hypothesis is that increasing immune reinfection probability will increase virus persistence.

If immune reinfection probability is higher, immune individuals can sometimes become infectious again before their immunity expires. This gives the virus more opportunities to continue spreading, especially after the initial susceptible population has decreased.

Therefore, the extended model is expected to show higher persistence rates and longer time to extinction as immune reinfection probability increases.
