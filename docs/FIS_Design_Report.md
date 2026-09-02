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

### 4. Defuzzification
The Centroid of Area (CoA) method is used to convert the aggregated fuzzy output into a crisp WPI score.

### 5. Conclusion
The FIS provides a robust, interpretable mechanism for classifying water potability, overcoming the limitations of rigid threshold-based methods. It acts as an edge-capable intelligent system suitable for low-cost IoT deployments.
