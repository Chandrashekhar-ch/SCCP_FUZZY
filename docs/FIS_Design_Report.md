# Fuzzy Inference System Design Report
## Water Potability Classification

### 1. Introduction
This report details the design and theoretical underpinning of the Mamdani Fuzzy Inference System (FIS) for assessing water potability. It aims to replace rigid threshold-based water quality checks with a system that can gracefully handle boundary conditions and sensor noise.

### 2. Fuzzy Sets and Membership Functions
The system utilizes fuzzy sets to represent the uncertainty and continuous nature of water quality parameters.
- **pH**: {ACIDIC, SLIGHTLY_ACIDIC, NEUTRAL, SLIGHTLY_ALKALINE, ALKALINE}
- **Turbidity**: {CLEAR, SLIGHTLY_TURBID, TURBID, VERY_TURBID}
- **TDS**: {PURE, ACCEPTABLE, HIGH, VERY_HIGH}
- **DO**: {VERY_LOW, LOW, ACCEPTABLE, HIGH}

The output variable is the Water Potability Index (WPI), ranging from 0 to 10.
- **WPI**: {NON_POTABLE, MARGINAL, POTABLE}

### 3. Rule Base
The rule base consists of 45 IF-THEN rules derived from WHO and BIS standards. 
- **Implication**: MIN operator
- **Aggregation**: MAX operator

#### 3.1 Expert Rules
1. IF (pH = NEUTRAL) AND (Turbidity = CLEAR) AND (TDS = ACCEPTABLE) AND (DO = HIGH) THEN WPI = POTABLE.
2. IF (pH = NEUTRAL) AND (Turbidity = CLEAR) AND (TDS = PURE) AND (DO = HIGH) THEN WPI = POTABLE.
3. IF (pH = NEUTRAL) AND (Turbidity = CLEAR) AND (TDS = ACCEPTABLE) AND (DO = ACCEPTABLE) THEN WPI = POTABLE.
4. IF (pH = SLIGHTLY_ALKALINE) AND (Turbidity = CLEAR) AND (TDS = ACCEPTABLE) AND (DO = HIGH) THEN WPI = POTABLE.
5. IF (pH = SLIGHTLY_ALKALINE) AND (Turbidity = CLEAR) AND (TDS = ACCEPTABLE) AND (DO = ACCEPTABLE) THEN WPI = POTABLE.
6. IF (pH = NEUTRAL) AND (Turbidity = CLEAR) AND (TDS = PURE) AND (DO = ACCEPTABLE) THEN WPI = POTABLE.
7. IF (pH = SLIGHTLY_ACIDIC) AND (Turbidity = CLEAR) AND (TDS = ACCEPTABLE) AND (DO = HIGH) THEN WPI = POTABLE.
8. IF (pH = SLIGHTLY_ACIDIC) AND (Turbidity = CLEAR) AND (TDS = PURE) AND (DO = HIGH) THEN WPI = POTABLE.
9. IF (pH = ACIDIC) THEN WPI = NON_POTABLE.
10. IF (pH = ALKALINE) THEN WPI = NON_POTABLE.
11. IF (Turbidity = VERY_TURBID) THEN WPI = NON_POTABLE.
12. IF (TDS = VERY_HIGH) THEN WPI = NON_POTABLE.
13. IF (DO = VERY_LOW) THEN WPI = NON_POTABLE.
14. IF (pH = SLIGHTLY_ACIDIC) AND (Turbidity = TURBID) AND (TDS = HIGH) THEN WPI = NON_POTABLE.
15. IF (Turbidity = TURBID) AND (TDS = HIGH) AND (DO = LOW) THEN WPI = NON_POTABLE.
16. IF (pH = SLIGHTLY_ALKALINE) AND (TDS = VERY_HIGH) AND (DO = LOW) THEN WPI = NON_POTABLE.
17. IF (pH = SLIGHTLY_ACIDIC) AND (TDS = VERY_HIGH) THEN WPI = NON_POTABLE.
18. IF (pH = NEUTRAL) AND (Turbidity = SLIGHTLY_TURBID) AND (TDS = ACCEPTABLE) AND (DO = ACCEPTABLE) THEN WPI = MARGINAL.
19. IF (pH = NEUTRAL) AND (Turbidity = CLEAR) AND (TDS = HIGH) AND (DO = ACCEPTABLE) THEN WPI = MARGINAL.
20. IF (pH = NEUTRAL) AND (Turbidity = CLEAR) AND (TDS = ACCEPTABLE) AND (DO = LOW) THEN WPI = MARGINAL.
21. IF (pH = SLIGHTLY_ALKALINE) AND (Turbidity = SLIGHTLY_TURBID) AND (TDS = ACCEPTABLE) AND (DO = ACCEPTABLE) THEN WPI = MARGINAL.
22. IF (pH = SLIGHTLY_ACIDIC) AND (Turbidity = CLEAR) AND (TDS = ACCEPTABLE) AND (DO = ACCEPTABLE) THEN WPI = MARGINAL.
23. IF (pH = NEUTRAL) AND (Turbidity = SLIGHTLY_TURBID) AND (TDS = HIGH) AND (DO = ACCEPTABLE) THEN WPI = MARGINAL.
24. IF (pH = SLIGHTLY_ALKALINE) AND (Turbidity = CLEAR) AND (TDS = HIGH) AND (DO = ACCEPTABLE) THEN WPI = MARGINAL.
25. IF (pH = SLIGHTLY_ACIDIC) AND (Turbidity = SLIGHTLY_TURBID) AND (TDS = ACCEPTABLE) AND (DO = ACCEPTABLE) THEN WPI = MARGINAL.
26. IF (pH = NEUTRAL) AND (Turbidity = CLEAR) AND (TDS = HIGH) AND (DO = HIGH) THEN WPI = MARGINAL.
27. IF (pH = NEUTRAL) AND (Turbidity = SLIGHTLY_TURBID) AND (TDS = PURE) AND (DO = HIGH) THEN WPI = MARGINAL.
28. IF (pH = SLIGHTLY_ALKALINE) AND (Turbidity = CLEAR) AND (TDS = PURE) AND (DO = LOW) THEN WPI = MARGINAL.
29. IF (pH = NEUTRAL) AND (Turbidity = TURBID) AND (TDS = ACCEPTABLE) AND (DO = ACCEPTABLE) THEN WPI = MARGINAL.
30. IF (pH = SLIGHTLY_ACIDIC) AND (Turbidity = CLEAR) AND (TDS = HIGH) AND (DO = ACCEPTABLE) THEN WPI = MARGINAL.
31. IF (pH = NEUTRAL) AND (Turbidity = TURBID) AND (TDS = ACCEPTABLE) AND (DO = HIGH) THEN WPI = MARGINAL.
32. IF (pH = NEUTRAL) AND (Turbidity = TURBID) AND (TDS = HIGH) AND (DO = LOW) THEN WPI = NON_POTABLE.
33. IF (pH = SLIGHTLY_ALKALINE) AND (Turbidity = TURBID) AND (TDS = HIGH) AND (DO = LOW) THEN WPI = NON_POTABLE.
34. IF (pH = SLIGHTLY_ACIDIC) AND (Turbidity = TURBID) AND (TDS = ACCEPTABLE) AND (DO = LOW) THEN WPI = NON_POTABLE.
35. IF (pH = ACIDIC) AND (Turbidity = VERY_TURBID) AND (TDS = VERY_HIGH) AND (DO = VERY_LOW) THEN WPI = NON_POTABLE.
36. IF (pH = ALKALINE) AND (Turbidity = TURBID) AND (TDS = VERY_HIGH) AND (DO = VERY_LOW) THEN WPI = NON_POTABLE.
37. IF (pH = NEUTRAL) AND (Turbidity = CLEAR) AND (TDS = PURE) AND (DO = VERY_LOW) THEN WPI = NON_POTABLE.
38. IF (pH = SLIGHTLY_ACIDIC) AND (Turbidity = SLIGHTLY_TURBID) AND (TDS = HIGH) AND (DO = LOW) THEN WPI = MARGINAL.
39. IF (pH = SLIGHTLY_ALKALINE) AND (Turbidity = SLIGHTLY_TURBID) AND (TDS = HIGH) AND (DO = LOW) THEN WPI = MARGINAL.
40. IF (pH = NEUTRAL) AND (Turbidity = SLIGHTLY_TURBID) AND (TDS = ACCEPTABLE) AND (DO = LOW) THEN WPI = MARGINAL.
41. IF (pH = SLIGHTLY_ALKALINE) AND (Turbidity = SLIGHTLY_TURBID) AND (TDS = PURE) AND (DO = ACCEPTABLE) THEN WPI = MARGINAL.
42. IF (pH = SLIGHTLY_ACIDIC) AND (Turbidity = CLEAR) AND (TDS = PURE) AND (DO = HIGH) THEN WPI = POTABLE.
43. IF (pH = SLIGHTLY_ALKALINE) AND (Turbidity = CLEAR) AND (TDS = ACCEPTABLE) AND (DO = LOW) THEN WPI = MARGINAL.
44. IF (pH = NEUTRAL) AND (Turbidity = TURBID) AND (TDS = PURE) AND (DO = LOW) THEN WPI = MARGINAL.
45. IF (pH = SLIGHTLY_ACIDIC) AND (Turbidity = SLIGHTLY_TURBID) AND (TDS = PURE) AND (DO = ACCEPTABLE) THEN WPI = MARGINAL.

### 4. Defuzzification
The Centroid of Area (CoA) method is used to convert the aggregated fuzzy output into a crisp WPI score.

### 5. Conclusion
The FIS provides a robust, interpretable mechanism for classifying water potability, overcoming the limitations of rigid threshold-based methods. It acts as an edge-capable intelligent system suitable for low-cost IoT deployments.
