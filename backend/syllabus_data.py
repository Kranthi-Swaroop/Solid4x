"""
Complete JEE syllabus data — Physics, Chemistry, Mathematics.
Each subject has chapters, each chapter has topics.
"""

JEE_SYLLABUS = {
    "Physics": [
        {
            "chapter": "Units & Measurements",
            "topics": ["SI Units", "Dimensional Analysis", "Significant Figures", "Errors in Measurement"]
        },
        {
            "chapter": "Kinematics",
            "topics": ["Motion in a Straight Line", "Motion in a Plane", "Projectile Motion", "Relative Motion", "Circular Motion"]
        },
        {
            "chapter": "Laws of Motion",
            "topics": ["Newton's Laws", "Free Body Diagrams", "Friction", "Pseudo Forces", "Circular Motion Dynamics"]
        },
        {
            "chapter": "Work, Energy & Power",
            "topics": ["Work-Energy Theorem", "Kinetic Energy", "Potential Energy", "Conservation of Energy", "Power", "Collisions"]
        },
        {
            "chapter": "Rotational Motion",
            "topics": ["Torque", "Moment of Inertia", "Angular Momentum", "Rolling Motion", "Equilibrium of Rigid Bodies"]
        },
        {
            "chapter": "Gravitation",
            "topics": ["Newton's Law of Gravitation", "Gravitational Potential", "Orbital Velocity", "Escape Velocity", "Kepler's Laws", "Satellites"]
        },
        {
            "chapter": "Properties of Solids & Fluids",
            "topics": ["Elasticity", "Stress & Strain", "Viscosity", "Surface Tension", "Bernoulli's Theorem", "Fluid Statics"]
        },
        {
            "chapter": "Thermodynamics",
            "topics": ["Zeroth Law", "First Law", "Second Law", "Carnot Engine", "Entropy", "Specific Heat Capacities"]
        },
        {
            "chapter": "Kinetic Theory of Gases",
            "topics": ["Ideal Gas Law", "Maxwell Distribution", "RMS Speed", "Degrees of Freedom", "Mean Free Path"]
        },
        {
            "chapter": "Oscillations",
            "topics": ["Simple Harmonic Motion", "Spring-Mass System", "Simple Pendulum", "Damped Oscillations", "Forced Oscillations & Resonance"]
        },
        {
            "chapter": "Waves",
            "topics": ["Wave Equation", "Superposition Principle", "Standing Waves", "Beats", "Doppler Effect", "Sound Waves"]
        },
        {
            "chapter": "Electrostatics",
            "topics": ["Coulomb's Law", "Electric Field", "Gauss's Law", "Electric Potential", "Capacitance", "Dielectrics", "Energy of Capacitors"]
        },
        {
            "chapter": "Current Electricity",
            "topics": ["Ohm's Law", "Kirchhoff's Laws", "Wheatstone Bridge", "Meter Bridge", "Potentiometer", "RC Circuits"]
        },
        {
            "chapter": "Magnetic Effects of Current",
            "topics": ["Biot-Savart Law", "Ampere's Law", "Force on Current-Carrying Conductor", "Solenoid & Toroid", "Moving Coil Galvanometer"]
        },
        {
            "chapter": "Electromagnetic Induction",
            "topics": ["Faraday's Law", "Lenz's Law", "Self Inductance", "Mutual Inductance", "AC Generator", "Eddy Currents"]
        },
        {
            "chapter": "Alternating Current",
            "topics": ["AC Circuits (R, L, C)", "Impedance & Resonance", "Power in AC", "Transformer", "LC Oscillations"]
        },
        {
            "chapter": "Electromagnetic Waves",
            "topics": ["Maxwell's Equations", "EM Wave Spectrum", "Properties of EM Waves", "Applications"]
        },
        {
            "chapter": "Ray Optics",
            "topics": ["Reflection", "Refraction", "Total Internal Reflection", "Lenses", "Mirrors", "Prism", "Optical Instruments"]
        },
        {
            "chapter": "Wave Optics",
            "topics": ["Interference", "Young's Double Slit", "Diffraction", "Polarization", "Brewster's Law"]
        },
        {
            "chapter": "Modern Physics",
            "topics": ["Photoelectric Effect", "Bohr Model", "X-rays", "de Broglie Wavelength", "Radioactivity", "Nuclear Fission & Fusion", "Mass-Energy Equivalence"]
        },
        {
            "chapter": "Semiconductor Electronics",
            "topics": ["p-n Junction Diode", "Zener Diode", "Transistor (NPN/PNP)", "Logic Gates", "Rectifiers"]
        },
    ],
    "Chemistry": [
        {
            "chapter": "Atomic Structure",
            "topics": ["Bohr's Model", "Quantum Numbers", "Electronic Configuration", "Aufbau Principle", "Photoelectric Effect"]
        },
        {
            "chapter": "Chemical Bonding",
            "topics": ["Ionic Bonding", "Covalent Bonding", "VSEPR Theory", "Hybridization", "Molecular Orbital Theory", "Hydrogen Bonding"]
        },
        {
            "chapter": "States of Matter",
            "topics": ["Gas Laws", "Ideal Gas Equation", "Kinetic Theory", "Real Gases", "Liquefaction"]
        },
        {
            "chapter": "Thermodynamics & Thermochemistry",
            "topics": ["Enthalpy", "Hess's Law", "Entropy", "Gibbs Free Energy", "Born-Haber Cycle", "Bond Energy"]
        },
        {
            "chapter": "Equilibrium",
            "topics": ["Law of Mass Action", "Le Chatelier's Principle", "Ionic Equilibrium", "pH & Buffers", "Solubility Product", "Common Ion Effect"]
        },
        {
            "chapter": "Redox Reactions & Electrochemistry",
            "topics": ["Balancing Redox Equations", "Electrochemical Cells", "Nernst Equation", "Conductance", "Electrolysis", "Corrosion"]
        },
        {
            "chapter": "Chemical Kinetics",
            "topics": ["Rate of Reaction", "Order & Molecularity", "Arrhenius Equation", "Activation Energy", "Catalysis", "Half-life"]
        },
        {
            "chapter": "Solutions",
            "topics": ["Concentration Terms", "Raoult's Law", "Colligative Properties", "Osmotic Pressure", "Van't Hoff Factor", "Ideal & Non-ideal Solutions"]
        },
        {
            "chapter": "Solid State",
            "topics": ["Crystal Systems", "Unit Cell", "Packing Efficiency", "Defects in Solids", "Electrical & Magnetic Properties"]
        },
        {
            "chapter": "Surface Chemistry",
            "topics": ["Adsorption", "Catalysis", "Colloids", "Emulsions", "Tyndall Effect"]
        },
        {
            "chapter": "Periodic Table & Properties",
            "topics": ["Periodic Trends", "Ionization Energy", "Electron Affinity", "Electronegativity", "Atomic & Ionic Radii"]
        },
        {
            "chapter": "s-Block Elements",
            "topics": ["Alkali Metals", "Alkaline Earth Metals", "Diagonal Relationship", "Compounds of Na, K, Ca, Mg"]
        },
        {
            "chapter": "p-Block Elements",
            "topics": ["Group 13 (Boron Family)", "Group 14 (Carbon Family)", "Group 15 (Nitrogen Family)", "Group 16 (Oxygen Family)", "Group 17 (Halogens)", "Group 18 (Noble Gases)", "Interhalogen Compounds"]
        },
        {
            "chapter": "d & f Block Elements",
            "topics": ["Transition Elements Properties", "Lanthanides", "Actinides", "KMnO4 & K2Cr2O7", "Magnetic Properties"]
        },
        {
            "chapter": "Coordination Chemistry",
            "topics": ["Werner's Theory", "IUPAC Nomenclature", "Isomerism", "Crystal Field Theory", "Stability Constants", "Applications"]
        },
        {
            "chapter": "General Organic Chemistry",
            "topics": ["Nomenclature (IUPAC)", "Isomerism", "Electronic Effects (Inductive, Resonance, Hyperconjugation)", "Reaction Intermediates", "Acid-Base Strength"]
        },
        {
            "chapter": "Hydrocarbons",
            "topics": ["Alkanes", "Alkenes", "Alkynes", "Aromatic Hydrocarbons", "Benzene Reactions", "Conformations"]
        },
        {
            "chapter": "Haloalkanes & Haloarenes",
            "topics": ["SN1 & SN2 Reactions", "Elimination Reactions", "Grignard Reagent", "Polyhalogen Compounds"]
        },
        {
            "chapter": "Alcohols, Phenols & Ethers",
            "topics": ["Preparation Methods", "Chemical Properties", "Acidity of Phenols", "Williamson Synthesis", "Electrophilic Substitution"]
        },
        {
            "chapter": "Aldehydes, Ketones & Carboxylic Acids",
            "topics": ["Nucleophilic Addition", "Aldol Condensation", "Cannizzaro Reaction", "Acidity of Carboxylic Acids", "Derivatives"]
        },
        {
            "chapter": "Amines",
            "topics": ["Classification", "Preparation", "Basicity", "Diazonium Salts", "Gabriel Synthesis", "Hofmann Bromamide"]
        },
        {
            "chapter": "Biomolecules",
            "topics": ["Carbohydrates", "Proteins & Amino Acids", "Nucleic Acids (DNA/RNA)", "Vitamins", "Enzymes"]
        },
        {
            "chapter": "Polymers",
            "topics": ["Classification", "Addition Polymers", "Condensation Polymers", "Natural & Synthetic Rubber", "Biodegradable Polymers"]
        },
        {
            "chapter": "Chemistry in Everyday Life",
            "topics": ["Drugs & Medicines", "Soaps & Detergents", "Food Preservatives", "Antioxidants"]
        },
    ],
    "Mathematics": [
        {
            "chapter": "Sets, Relations & Functions",
            "topics": ["Types of Sets", "Venn Diagrams", "Relations", "Types of Functions", "Composition of Functions", "Inverse Functions"]
        },
        {
            "chapter": "Complex Numbers",
            "topics": ["Algebra of Complex Numbers", "Argand Plane", "Modulus & Argument", "De Moivre's Theorem", "Roots of Unity", "Geometry of Complex Numbers"]
        },
        {
            "chapter": "Quadratic Equations",
            "topics": ["Roots & Discriminant", "Nature of Roots", "Relation between Roots & Coefficients", "Equations Reducible to Quadratics", "Maximum & Minimum Values"]
        },
        {
            "chapter": "Sequences & Series",
            "topics": ["Arithmetic Progression", "Geometric Progression", "Harmonic Progression", "AGP", "Summation of Series", "Mathematical Induction"]
        },
        {
            "chapter": "Permutations & Combinations",
            "topics": ["Fundamental Counting Principle", "Permutations", "Combinations", "Circular Permutations", "Division & Distribution", "Derangements"]
        },
        {
            "chapter": "Binomial Theorem",
            "topics": ["Binomial Expansion", "General Term", "Middle Term", "Properties of Binomial Coefficients", "Multinomial Theorem"]
        },
        {
            "chapter": "Matrices & Determinants",
            "topics": ["Types of Matrices", "Matrix Operations", "Determinant Properties", "Adjoint & Inverse", "Solving Linear Equations (Cramer's Rule)", "Rank of Matrix"]
        },
        {
            "chapter": "Trigonometry",
            "topics": ["Trigonometric Ratios & Identities", "Trigonometric Equations", "Inverse Trigonometric Functions", "Properties of Triangles", "Heights & Distances"]
        },
        {
            "chapter": "Coordinate Geometry — Straight Lines",
            "topics": ["Distance & Section Formulae", "Slope & Equations of Lines", "Angle Between Lines", "Pair of Straight Lines", "Concurrency & Family of Lines"]
        },
        {
            "chapter": "Coordinate Geometry — Circles",
            "topics": ["Equation of Circle", "Tangent & Normal", "Chord of Contact", "Family of Circles", "Radical Axis", "Power of a Point"]
        },
        {
            "chapter": "Coordinate Geometry — Conics",
            "topics": ["Parabola", "Ellipse", "Hyperbola", "Tangents & Normals to Conics", "Eccentricity", "Latus Rectum"]
        },
        {
            "chapter": "3D Geometry",
            "topics": ["Direction Cosines & Ratios", "Equation of Line in 3D", "Equation of Plane", "Angle Between Line & Plane", "Shortest Distance", "Coplanarity"]
        },
        {
            "chapter": "Vectors",
            "topics": ["Vector Algebra", "Dot Product", "Cross Product", "Scalar Triple Product", "Vector Triple Product", "Applications"]
        },
        {
            "chapter": "Limits, Continuity & Differentiability",
            "topics": ["Limits (Algebraic, Trigonometric, Exponential)", "L'Hôpital's Rule", "Continuity", "Differentiability", "Intermediate Value Theorem"]
        },
        {
            "chapter": "Differentiation",
            "topics": ["First Principles", "Chain Rule", "Product & Quotient Rule", "Implicit Differentiation", "Logarithmic Differentiation", "Higher Order Derivatives", "Parametric Differentiation"]
        },
        {
            "chapter": "Application of Derivatives",
            "topics": ["Tangent & Normal", "Rate of Change", "Maxima & Minima", "Increasing & Decreasing Functions", "Rolle's & Mean Value Theorem", "Curve Sketching"]
        },
        {
            "chapter": "Indefinite Integration",
            "topics": ["Basic Integrals", "Integration by Substitution", "Integration by Parts", "Partial Fractions", "Special Integrals", "Reduction Formulae"]
        },
        {
            "chapter": "Definite Integration",
            "topics": ["Properties of Definite Integrals", "Leibniz Rule", "Walli's Formula", "Gamma Function", "Integration as Limit of Sum"]
        },
        {
            "chapter": "Area Under Curves",
            "topics": ["Area Between Curves", "Area Using Integration", "Standard Curves"]
        },
        {
            "chapter": "Differential Equations",
            "topics": ["Order & Degree", "Variable Separable", "Homogeneous Equations", "Linear Differential Equations", "Bernoulli's Equation", "Applications"]
        },
        {
            "chapter": "Probability",
            "topics": ["Classical Probability", "Conditional Probability", "Bayes' Theorem", "Binomial Distribution", "Mean & Variance", "Independent Events"]
        },
        {
            "chapter": "Statistics",
            "topics": ["Mean, Median, Mode", "Standard Deviation", "Variance", "Frequency Distribution"]
        },
    ],
}


def get_total_topic_count():
    """Return total number of topics across all subjects."""
    total = 0
    for subject_chapters in JEE_SYLLABUS.values():
        for chapter in subject_chapters:
            total += len(chapter["topics"])
    return total
