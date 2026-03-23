"""
Build structured JEE syllabus from backend/data/filters.json.
Maps subjects → chapter groups → chapters → topics.
"""
import json
from pathlib import Path

_FILTERS_PATH = Path(__file__).parent / "data" / "filters.json"

# ── Subject → Chapter-Group mapping ──
SUBJECT_GROUPS = {
    "mathematics": ["trigonometry", "algebra", "calculus", "coordinate-geometry"],
    "physics": ["mechanics", "optics", "electricity", "modern-physics"],
    "chemistry": ["physical-chemistry", "organic-chemistry", "inorganic-chemistry"],
}

# ── Chapter-Group → Chapters mapping ──
GROUP_CHAPTERS = {
    # Mathematics
    "trigonometry": [
        "trigonometric-ratio-and-identites", "trigonometric-functions-and-equations",
        "inverse-trigonometric-functions", "properties-of-triangle", "height-and-distance",
    ],
    "algebra": [
        "sets-and-relations", "functions", "complex-numbers", "quadratic-equation-and-inequalities",
        "permutations-and-combinations", "binomial-theorem", "sequences-and-series",
        "matrices-and-determinants", "probability", "logarithm", "mathematical-induction",
        "mathematical-reasoning", "statistics",
    ],
    "calculus": [
        "limits-continuity-and-differentiability", "differentiation", "application-of-derivatives",
        "indefinite-integrals", "definite-integration", "area-under-the-curves",
        "differential-equations",
    ],
    "coordinate-geometry": [
        "straight-lines-and-pair-of-straight-lines", "circle", "parabola", "ellipse",
        "hyperbola", "3d-geometry", "vector-algebra",
    ],
    # Physics
    "mechanics": [
        "units-and-measurements", "motion-in-a-straight-line", "motion-in-a-plane",
        "laws-of-motion", "work-power-and-energy", "center-of-mass", "rotational-motion",
        "gravitation", "properties-of-matter", "simple-harmonic-motion", "waves",
        "circular-motion", "heat-and-thermodynamics",
    ],
    "optics": [
        "geometrical-optics", "wave-optics",
    ],
    "electricity": [
        "electrostatics", "capacitor", "current-electricity", "magnetics",
        "electromagnetic-induction", "alternating-current", "electromagnetic-waves",
        "magnetic-properties-of-matter",
    ],
    "modern-physics": [
        "dual-nature-of-radiation", "atoms-and-nuclei", "electronic-devices",
        "communication-systems",
    ],
    # Chemistry
    "physical-chemistry": [
        "some-basic-concepts-of-chemistry", "structure-of-atom", "gaseous-state",
        "thermodynamics", "chemical-equilibrium", "ionic-equilibrium", "solutions",
        "redox-reactions", "electrochemistry", "chemical-kinetics-and-nuclear-chemistry",
        "solid-state", "surface-chemistry",
    ],
    "organic-chemistry": [
        "basics-of-organic-chemistry", "hydrocarbons", "haloalkanes-and-haloarenes",
        "alcohols-phenols-and-ethers", "aldehydes-ketones-and-carboxylic-acids",
        "compounds-containing-nitrogen", "biomolecules", "polymers",
        "chemistry-in-everyday-life", "practical-organic-chemistry",
    ],
    "inorganic-chemistry": [
        "periodic-table-and-periodicity", "chemical-bonding-and-molecular-structure",
        "hydrogen", "s-block-elements", "p-block-elements", "d-and-f-block-elements",
        "coordination-compounds", "isolation-of-elements", "salt-analysis",
        "environmental-chemistry",
    ],
}

# ── Chapter → Topics mapping ──
CHAPTER_TOPICS = {
    # MATHEMATICS — Trigonometry
    "trigonometric-ratio-and-identites": [
        "addition-and-subtraction-formula", "range-of-trigonometric-functions",
        "fundamental-identities", "multiple-and-sub-multiple-angle-formula",
        "transformation-formula", "trigonometric-series", "summation-series-problems",
        "trigonometric-ratio-of-standard-angles", "reduction-formula",
        "basic-definition-of-trigonometric-function",
    ],
    "trigonometric-functions-and-equations": [
        "solving-trigonometric-equations",
        "general-solution-and-principal-solution-of-the-equation",
    ],
    "inverse-trigonometric-functions": [
        "properties-of-inverse-trigonometric-functions",
        "domain-and-range-of-inverse-trigonometric-functions",
        "principal-value-of-inverse-trigonometric-functions",
        "sum-upto-n-terms-and-infinite-terms-of-inverse-series",
    ],
    "properties-of-triangle": [
        "cosine-rule", "ex-circle", "half-angle-formulae", "mediun-and-angle-bisector",
        "area-of-triangle", "circumcenter-incenter-and-orthocenter", "sine-rule",
    ],
    "height-and-distance": ["height-and-distance"],
    # MATHEMATICS — Algebra
    "sets-and-relations": [
        "symmetric-transitive-and-reflexive-properties", "venn-diagram",
        "number-of-sets-and-relations", "venn-diagram-and-set-theory",
    ],
    "functions": [
        "periodic-functions", "domain", "even-and-odd-functions",
        "classification-of-functions", "functional-equations", "range",
        "composite-functions", "inverse-functions",
    ],
    "complex-numbers": [
        "algebra-of-complex-numbers", "argument-of-complex-numbers",
        "applications-of-complex-numbers-in-coordinate-geometry", "de-moivres-theorem",
        "cube-roots-of-unity", "modulus-of-complex-numbers", "nth-roots-of-unity",
        "conjugate-of-complex-numbers", "square-root-of-a-complex-number",
    ],
    "quadratic-equation-and-inequalities": [
        "modulus-function", "relation-between-roots-and-coefficients", "inequalities",
        "common-roots", "nature-of-roots", "graph-and-sign-of-quadratic-expression",
        "range-of-quadratic-expression", "location-of-roots",
        "greatest-integer-and-fractional-part-functions",
        "algebraic-equations-of-higher-degree",
    ],
    "permutations-and-combinations": [
        "conditional-permutations", "divisibility-of-numbers", "conditional-combinations",
        "circular-permutations", "number-of-combinations", "number-of-permutations",
        "factorial", "application-of-permutations-and-combination-in-geometry",
        "dearrangement", "sum-of-numbers",
    ],
    "binomial-theorem": [
        "problems-based-on-binomial-co-efficient-and-collection-of-binomial-co-efficient",
        "general-term", "binomial-theorem-for-any-index", "negative-and-fractional-index",
        "middle-term", "divisibility-concept-and-remainder-concept",
        "integral-and-fractional-part-of-a-number", "multinomial-theorem",
    ],
    "sequences-and-series": [
        "geometric-progression", "arithmetic-progression", "summation-of-series",
        "harmonic-progression", "am-gm-and-hm", "arithmetico-geometric-progression",
    ],
    "matrices-and-determinants": [
        "expansion-of-determinant", "multiplication-of-matrices",
        "solutions-of-system-of-linear-equations-in-two-or-three-variables-using-determinants-and-matrices",
        "inverse-of-a-matrix", "operations-on-matrices", "properties-of-determinants",
        "trace-of-a-matrix", "basic-of-matrix", "symmetric-and-skew-symmetric-matrices",
        "transpose-of-a-matrix", "adjoint-of-a-matrix",
    ],
    "probability": [
        "binomial-distribution", "classical-defininition-of-probability",
        "probability-distribution-of-a-random-variable",
        "conditional-probability-and-multiplication-theorem",
        "permutation-and-combination-based-problem", "total-probability-theorem",
        "bayes-theorem",
    ],
    "logarithm": ["logarithmic-equations", "logarithm-inequalities"],
    "mathematical-induction": ["mathematical-induction"],
    "mathematical-reasoning": ["logical-statement", "logical-connectives"],
    "statistics": [
        "calculation-of-mean-median-and-mode-of-grouped-and-ungrouped-data",
        "calculation-of-standard-deviation-variance-and-mean-deviation-of-grouped-and-ungrouped-data",
    ],
    # MATHEMATICS — Calculus
    "limits-continuity-and-differentiability": [
        "limits-of-algebric-function", "limits-of-trigonometric-functions",
        "limits-of-exponential-functions", "limits-of-logarithmic-functions",
        "continuity", "differentiability", "existance-of-limits",
    ],
    "differentiation": [
        "differentiation-of-implicit-function", "successive-differentiation",
        "differentiation-of-logarithmic-function", "differentiation-of-composite-function",
        "methods-of-differentiation", "differentiation-of-inverse-trigonometric-function",
        "differentiation-of-a-function-with-respect-to-another-function",
        "differentiation-of-parametric-function",
    ],
    "application-of-derivatives": [
        "maxima-and-minima", "mean-value-theorem", "rate-of-change-of-quantity", "monotonicity",
    ],
    "indefinite-integrals": [
        "standard-integral", "integration-by-substitution", "integration-by-parts",
        "integration-by-partial-fraction",
    ],
    "definite-integration": [
        "definite-integral-as-a-limit-of-sum", "properties-of-definite-integration",
        "newton-lebnitz-rule-of-differentiation",
    ],
    "area-under-the-curves": [
        "area-bounded-between-the-curves", "area-under-simple-curves-in-standard-forms",
    ],
    "differential-equations": [
        "solution-of-differential-equations-by-method-of-separation-variables-and-homogeneous",
        "order-and-degree", "linear-differential-equations", "formation-of-differential-equations",
    ],
    # MATHEMATICS — Coordinate Geometry
    "straight-lines-and-pair-of-straight-lines": [
        "pair-of-straight-lines", "locus", "distance-formula", "various-forms-of-straight-line",
        "centers-of-triangle", "position-of-a-point-with-respect-to-a-line", "angle-bisector",
        "area-of-triangle-and-condition-of-collinearity", "section-formula",
        "distance-of-a-point-from-a-line", "angle-between-two-lines",
        "family-of-straight-line", "condition-of-concurrency",
    ],
    "circle": [
        "chord-with-a-given-middle-point", "basic-theorems-of-a-circle", "family-of-circle",
        "number-of-common-tangents-and-position-of-two-circle", "orthogonality-of-two-circles",
        "radical-axis", "intercepts-of-a-circle", "position-of-a-point-with-respect-to-circle",
        "tangent-and-normal", "director-circle", "parametric-form-of-a-circle",
    ],
    "parabola": [
        "common-tangent", "normal-to-parabola", "chord-of-parabola",
        "question-based-on-basic-definition-and-parametric-representation",
        "tangent-to-parabola", "chord-of-contact",
        "position-of-point-and-chord-joining-of-two-points", "pair-of-tangents",
    ],
    "ellipse": ["tangent-to-ellipse", "normal-to-ellipse", "chord-of-ellipse"],
    "hyperbola": ["tangent-to-hyperbola", "normal-to-hyperbola"],
    "3d-geometry": [
        "lines-and-plane", "plane-in-space",
        "direction-cosines-and-direction-ratios-of-a-line", "lines-in-space",
    ],
    "vector-algebra": [
        "dot-product-and-cross-product", "vector-arithmetic", "vector-projections",
    ],
    # PHYSICS — Mechanics
    "units-and-measurements": [
        "dimensions-of-physical-quantities", "errors-in-measurement",
        "screw-gauge", "vernier-calipers", "unit-of-physical-quantities",
    ],
    "motion-in-a-straight-line": [
        "motion-under-gravity", "constant-acceleration-motion",
        "average-velocity-and-instantaneous-velocity", "variable-acceleration-motion",
        "graph-based-problem", "relative-motion-in-one-dimension",
        "average-acceleration-and-instantaneous-acceleration",
        "average-speed-and-instantaneous-speed",
    ],
    "motion-in-a-plane": [
        "projectile-motion", "relative-motion-in-two-dimension",
        "river-boat-problems", "rain-man-problems",
    ],
    "laws-of-motion": [
        "equilibrium-of-a-particle", "newtons-laws-of-motion",
        "motion-of-connected-bodies", "friction-force",
        "motion-on-an-inclined-plane", "spring-force",
    ],
    "work-power-and-energy": ["energy", "work", "power"],
    "center-of-mass": [
        "motion-of-center-of-mass", "impulse-momentum-theorem",
        "center-of-mass-of-continuous-mass-distribution", "collision",
        "center-of-mass-of-discrete-particles", "cavity-problems", "spring-mass-system",
    ],
    "rotational-motion": [
        "moment-of-inertia", "angular-momentum",
        "combined-translational-and-rotational-motion", "torque",
        "rotational-motion-about-fixed-axis-of-rigid-body", "angular-momentum-conservation",
    ],
    "gravitation": [
        "escape-speed-and-motion-of-satellites", "keplers-law-and-universal-law-of-gravitation",
        "gravitational-potential-and-gravitational-potential-energy",
        "acceleration-due-to-gravity-and-its-variation",
    ],
    "properties-of-matter": [
        "fluid-flow-bernoullis-principle-and-viscosity", "newtons-law-of-cooling",
        "mechanical-properties-of-solids", "surface-tension-excess-pressure-and-capillarity",
        "stress-strain-curve-thermal-stress-and-elastic-pe",
        "pressure-density-pascals-law-and-archimedes-principle",
    ],
    "simple-harmonic-motion": [
        "simple-harmonic-motion", "some-systems-of-executing-shm",
        "forced-damped-oscillations-and-resonance",
    ],
    "waves": [
        "superposition-and-reflection-of-waves", "basic-of-waves-and-progressive-waves",
        "doppler-effect",
    ],
    "circular-motion": ["uniform-circular-motion", "non-uniform-circular-motion"],
    "heat-and-thermodynamics": [
        "heat-engine-second-law-of-thermodynamics-and-carnot-engine", "heat-transfer",
        "specific-heat-capacity-calorimetry-and-change-of-state",
        "kinetic-theory-of-gases-and-gas-laws", "thermodynamics-process",
        "zeroth-and-first-law-of-thermodynamics",
        "degree-of-freedom-and-law-of-equipartition-of-energy",
        "thermometry-and-thermal-expansion",
    ],
    # PHYSICS — Optics
    "geometrical-optics": [
        "reflection-of-light", "optical-instruments",
        "refraction-tir-and-prism", "lenses",
    ],
    "wave-optics": [
        "huygens-principle-and-interference-of-light", "polarisation",
        "diffraction-and-doppler-effect-of-light",
    ],
    # PHYSICS — Electricity & Magnetism
    "electrostatics": [
        "electric-potential-energy-and-electric-potential", "electric-flux-and-gauss-law",
        "electric-charges-and-coulombs-law", "electric-field-and-electric-field-intensity",
        "electric-dipole",
    ],
    "capacitor": [
        "electric-energy-stored-by-capacitor", "capacitance", "capacitors-with-dielectric",
        "combination-of-capacitors", "parallel-plate-capacitor", "rc-circuit",
        "capacitor-in-circuit",
    ],
    "current-electricity": [
        "galvanometer-voltmeter-and-ammeter", "electric-power-and-heating-effect-of-current",
        "electric-cell-or-battery", "resistance-and-resistivity", "kirchhoffs-circuit-laws",
        "potentiometer", "combination-of-resistances", "meter-bridge", "ohms-law",
        "electric-current-current-density-and-drift-velocity", "wheatstone-bridge",
        "color-coding-of-resistance",
    ],
    "magnetics": [
        "biot-savarts-law-and-magnetic-field-due-to-current-carrying-wire",
        "motion-of-charged-particle-inside-magnetic-field",
        "force-and-torque-on-current-carrying-conductor", "amperes-circuital-law",
        "magnetic-moment", "moving-coil-galvanometer", "magnetic-field-of-moving-charge",
    ],
    "electromagnetic-induction": [
        "inductance-self-and-mutual", "motional-emf-and-eddy-current",
        "magnetic-flux-faradays-and-lenzs-laws",
    ],
    "alternating-current": [
        "ac-generator-and-transformer", "ac-circuits-and-power-in-ac-circuits",
        "growth-and-decay-of-current", "quality-factor",
    ],
    "electromagnetic-waves": [
        "displacement-current-and-properties-of-em-waves", "em-spectrum",
    ],
    "magnetic-properties-of-matter": [
        "bar-magnet-or-magnetic-dipole", "earth-magnetism", "magnetic-properties-of-matter",
    ],
    # PHYSICS — Modern Physics
    "dual-nature-of-radiation": [
        "photoelectric-effect", "matter-waves-davisson-and-germer-experiment",
        "particle-nature-of-light-the-photon", "davisson-and-germer-experiment",
    ],
    "atoms-and-nuclei": [
        "nucleus-and-radioactivity", "bohrs-model-and-hydrogen-spectrum",
        "nuclear-fission-and-fusion-and-binding-energy",
        "alpha-particle-scattering-and-rutherford-model-of-atom",
    ],
    "electronic-devices": [
        "semiconductor-and-p-n-junction-diode", "transistors", "digital-circuits",
    ],
    "communication-systems": [
        "elements-of-communication-system-and-propagation-of-em-wave",
        "modulation-and-demodulation",
    ],
    # CHEMISTRY — Physical
    "some-basic-concepts-of-chemistry": [
        "quantitative-measures-in-chemical-equations", "concentration-terms",
        "mole-concept", "laws-of-chemical-combination", "significant-figures",
    ],
    "structure-of-atom": [
        "bohrs-model-for-hydrogen-atom", "heisenberg-uncertainty-principle",
        "electronic-configuration-and-nodes", "de-broglie-hypothesis",
        "quantum-numbers-and-orbitals", "hydrogen-spectrum",
        "quantum-mechanical-model-of-atom", "thomsons-model-and-rutherfords-model",
    ],
    "gaseous-state": [
        "ideal-gas-equation", "kinetic-theory-of-gases", "real-gas-and-van-der-walls-equation",
        "maxwells-distribution-of-speed", "daltons-law-of-partial-pressure",
        "gas-laws", "critical-phenomenon-and-liquefaction",
    ],
    "thermodynamics": [
        "reactions-related-to-enthalpies-and-hesss-law",
        "entropy-free-energy-change-and-spontaneity",
        "first-law-of-thermodynamics", "fundamentals-of-thermodynamics",
        "second-law-of-thermodynamics",
    ],
    "chemical-equilibrium": [
        "chemical-equilibrium-law-of-mass-action-and-equilibrium-constant",
        "le-chateliers-principle-and-factors-affecting-chemical-equilibrium",
    ],
    "ionic-equilibrium": [
        "ostwalds-dilution-law-and-concept-of-acid-and-base",
        "ph-buffer-and-indicators", "solubility-product-and-common-ion-effect",
        "salt-hydrolysis",
    ],
    "solutions": [
        "relative-lowering-of-vapour-pressure-and-roults-law",
        "depression-in-freezing-point", "elevation-in-boiling-point",
        "abnormal-colligative-property-and-vant-hoff-factor",
        "osmotic-pressure", "henrys-law",
    ],
    "redox-reactions": [
        "oxidation-and-reduction-reactions", "balancing-of-redox-reactions",
        "equivalence", "redox-titration", "oxidation-number", "types-of-redox-reactions",
    ],
    "electrochemistry": [
        "conductance-and-electrolysis", "electrochemical-series-cell-and-their-emf",
        "batteries-fuel-cells-and-corrosion",
    ],
    "chemical-kinetics-and-nuclear-chemistry": [
        "rate-laws-and-rate-constant", "integrated-rate-law-equations", "nuclear-chemistry",
        "rate-of-reaction", "arrhenius-equation",
        "different-methods-to-determine-order-of-reaction",
    ],
    "solid-state": [
        "crystal-structure-of-solids", "structure-of-ionic-compounds",
        "defects-in-crystal", "close-packing-in-crystals",
        "type-of-solids-and-their-properties", "interestitial-voids",
    ],
    "surface-chemistry": ["adsorption", "colloids", "catalysis"],
    # CHEMISTRY — Organic
    "basics-of-organic-chemistry": [
        "isomerism", "electron-displacement-effect", "iupac-nomenclature",
        "acid-and-base-strength", "stability-of-intermediate",
        "purification-of-organic-compounds", "aromaticity",
    ],
    "hydrocarbons": [
        "reaction-of-alkynes", "reaction-of-alkenes", "reaction-of-alkanes",
        "properties-and-preparation-of-alkanes", "properties-and-preparation-of-alkenes",
        "aromatic-hydrocarbons", "properties-and-preparation-of-alkynes",
    ],
    "haloalkanes-and-haloarenes": [
        "haloalkanes", "haloarenes", "some-important-polyhalogens-compounds",
    ],
    "alcohols-phenols-and-ethers": [
        "properties-preparation-and-uses-of-ethers",
        "properties-preparation-and-uses-of-alcohols",
        "properties-preparation-and-uses-of-phenols",
    ],
    "aldehydes-ketones-and-carboxylic-acids": [
        "preparation-properties-and-uses-of-carboxylic-acids",
        "preparation-methods-for-both-aldehydes-and-ketones",
        "reactions-involving-aldehydes", "chemical-reactions-for-aldehydes-and-ketones",
        "method-of-preparation-for-aldehydes", "tests-for-aldehyde-and-ketones",
    ],
    "compounds-containing-nitrogen": [
        "diazonium-salts-and-other-nitrogen-containing-compounds",
        "aliphatic-amines", "aromatic-amines",
    ],
    "biomolecules": [
        "proteins-and-enzymes", "vitamins-and-nucleic-acids", "carbohydrates", "hydrolysis",
    ],
    "polymers": [
        "uses-of-polymers", "classification-preparations-and-properties-of-polymers",
    ],
    "chemistry-in-everyday-life": [
        "chemicals-in-medicines", "cleansing-agents", "chemicals-in-foods",
    ],
    "practical-organic-chemistry": [
        "chemistry-involved-in-the-preparation-of-organic-and-inorganic-compounds",
        "detection-of-extra-elements-and-functional-groups",
        "qualitative-salt-analysis", "chemistry-involved-in-titrimetric-experiments",
        "experiments-involving-physical-chemistry",
    ],
    # CHEMISTRY — Inorganic
    "periodic-table-and-periodicity": [
        "atomic-and-ionic-radius", "periodic-table-and-its-features",
        "ionization-energy", "nature-of-oxide", "electronegativity",
        "electron-gain-enthalpy", "effective-nuclear-charge",
    ],
    "chemical-bonding-and-molecular-structure": [
        "hybridization-and-vsepr-theory", "molecular-orbital-theory",
        "covalent-and-co-ordinate-bond", "dipole-moment", "bond-parameters",
        "ionic-bond", "hydrogen-bonding", "back-bonding", "valence-bond-theory",
        "lewis-theory", "van-der-walls-forces", "resonance",
    ],
    "hydrogen": [
        "hard-and-soft-water", "preparation-and-properties-of-hydrogen",
        "hydrogen-peroxide", "water-and-heavy-water", "hydrides",
    ],
    "s-block-elements": [
        "physiochemical-trends-in-alkali-metals", "compounds-of-alkali-metals",
        "physiochemical-trends-in-alkaline-earth-metals", "compounds-of-alkaline-earth-metals",
    ],
    "p-block-elements": [
        "group-18-elements-inert-or-noble-gases", "group-15-elements-nitrogen-family",
        "group-16-elements-oxygen-family", "group-17-elements-halogen-family",
        "group-14-elements-carbon-family", "group-13-elements-boron-family",
    ],
    "d-and-f-block-elements": [
        "important-compounds-of-transition-elements",
        "inner-transition-elements-lanthanoids-and-actinoids",
        "properties-of-transition-elements",
    ],
    "coordination-compounds": [
        "crystal-field-theory-cft",
        "application-of-coordination-compound-and-organometallic-compounds",
        "isomerism-of-coordination-compounds", "coordination-number",
        "warners-theory-and-valence-bond-theory",
        "nomenclature-of-coordination-compounds",
    ],
    "isolation-of-elements": [
        "extractions-of-metals", "concentration-of-ore",
        "refining-or-purification-of-metal", "minerals-and-ores", "ellingham-diagram",
    ],
    "salt-analysis": [
        "systematic-analysis-of-cations", "chemical-principles",
        "systematic-analysis-of-anions", "flame-and-charcoal-tests",
        "preliminary-tests", "introduction-to-qualitative-analysis",
    ],
    "environmental-chemistry": [
        "air-pollution", "environmental-pollution", "water-pollution", "soil-pollution",
    ],
}


def _slug_to_title(slug: str) -> str:
    """Convert 'some-slug-name' → 'Some Slug Name'."""
    return slug.replace("-", " ").title()


def get_structured_syllabus():
    """Return the structured syllabus: {subject: [{group, chapters: [{chapter, topics}]}]}."""
    result = {}
    for subject_slug, groups in SUBJECT_GROUPS.items():
        subject_name = _slug_to_title(subject_slug)
        subject_data = []
        for group_slug in groups:
            chapters_in_group = GROUP_CHAPTERS.get(group_slug, [])
            chapter_list = []
            for ch_slug in chapters_in_group:
                topics = CHAPTER_TOPICS.get(ch_slug, [])
                chapter_list.append({
                    "chapter": _slug_to_title(ch_slug),
                    "chapter_slug": ch_slug,
                    "topics": [{"name": _slug_to_title(t), "slug": t} for t in topics if t],
                })
            subject_data.append({
                "group": _slug_to_title(group_slug),
                "group_slug": group_slug,
                "chapters": chapter_list,
            })
        result[subject_name] = subject_data
    return result


def get_total_topic_count():
    """Return total number of topics across all subjects."""
    total = 0
    for groups in get_structured_syllabus().values():
        for group in groups:
            for chapter in group["chapters"]:
                total += len(chapter["topics"])
    return total
