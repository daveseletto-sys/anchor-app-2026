"""
Medical sources and references for the Anchor Recovery app.
Used to comply with Apple App Store Guideline 1.4.1 (Safety - Physical Harm)
which requires medical claims to be backed by authoritative citations.
"""

# Glossary terms enriched with sources. Each medical term has at least one authoritative source.
GLOSSARY = [
    {"term": "AA (Alcoholics Anonymous)", "definition": "An international fellowship of people who share their experience, strength, and hope with each other to recover from alcoholism, using a 12-step program.",
     "source_name": "Alcoholics Anonymous", "source_url": "https://www.aa.org/what-is-aa"},
    {"term": "Abstinence", "definition": "The practice of completely avoiding alcohol and other addictive substances.",
     "source_name": "NIAAA", "source_url": "https://www.niaaa.nih.gov/alcohols-effects-health/alcohol-use-disorder"},
    {"term": "Alcohol Use Disorder (AUD)", "definition": "A medical condition characterized by an impaired ability to stop or control alcohol use despite adverse social, occupational, or health consequences.",
     "source_name": "National Institute on Alcohol Abuse and Alcoholism (NIAAA)", "source_url": "https://www.niaaa.nih.gov/alcohols-effects-health/alcohol-use-disorder"},
    {"term": "ALT (Alanine Aminotransferase)", "definition": "A liver enzyme. Elevated ALT often indicates liver inflammation or damage. Normal range: approximately 7–56 U/L.",
     "source_name": "MedlinePlus (NIH)", "source_url": "https://medlineplus.gov/lab-tests/alanine-transaminase-alt-blood-test/"},
    {"term": "AST (Aspartate Aminotransferase)", "definition": "A liver enzyme that can also be found in heart and muscles. Elevated AST may indicate liver damage. Normal range: approximately 10–40 U/L.",
     "source_name": "MedlinePlus (NIH)", "source_url": "https://medlineplus.gov/lab-tests/aspartate-aminotransferase-ast-test/"},
    {"term": "Bilirubin", "definition": "A yellow compound produced by the breakdown of red blood cells. High bilirubin can indicate liver problems or biliary obstruction.",
     "source_name": "MedlinePlus (NIH)", "source_url": "https://medlineplus.gov/lab-tests/bilirubin-blood-test/"},
    {"term": "Cirrhosis", "definition": "Late-stage scarring (fibrosis) of the liver caused by many forms of liver disease and conditions, including chronic alcohol use.",
     "source_name": "Mayo Clinic", "source_url": "https://www.mayoclinic.org/diseases-conditions/cirrhosis/symptoms-causes/syc-20351487"},
    {"term": "Craving", "definition": "A strong desire or urge to drink alcohol; a hallmark of alcohol dependence.",
     "source_name": "NIAAA", "source_url": "https://www.niaaa.nih.gov/alcohols-effects-health/alcohol-use-disorder"},
    {"term": "Detoxification (Detox)", "definition": "The process by which the body clears itself of alcohol or drugs. Medical detox may be required for safety when stopping heavy drinking.",
     "source_name": "SAMHSA", "source_url": "https://www.samhsa.gov/find-help/national-helpline"},
    {"term": "Dehydration", "definition": "A condition that occurs when you lose more fluids than you take in. Alcohol is a diuretic and contributes to dehydration.",
     "source_name": "Mayo Clinic", "source_url": "https://www.mayoclinic.org/diseases-conditions/dehydration/symptoms-causes/syc-20354086"},
    {"term": "Fatty Liver Disease", "definition": "A condition in which excess fat builds up in the liver. Alcoholic fatty liver disease is one of the earliest stages of alcohol-related liver disease.",
     "source_name": "NHS UK", "source_url": "https://www.nhs.uk/conditions/alcohol-related-liver-disease-arld/"},
    {"term": "GABA", "definition": "A neurotransmitter affected by alcohol. Long-term drinking dysregulates GABA, contributing to withdrawal symptoms.",
     "source_name": "NIAAA — Neuroscience of Alcohol", "source_url": "https://pubs.niaaa.nih.gov/publications/arh313/185-195.htm"},
    {"term": "GGT (Gamma-Glutamyl Transferase)", "definition": "A liver enzyme often elevated in alcohol-related liver disease and biliary issues. Normal range: approximately 9–48 U/L.",
     "source_name": "MedlinePlus (NIH)", "source_url": "https://medlineplus.gov/lab-tests/gamma-glutamyl-transferase-ggt-test/"},
    {"term": "Harm Reduction", "definition": "A set of practical strategies and ideas aimed at reducing negative consequences associated with drug or alcohol use.",
     "source_name": "SAMHSA", "source_url": "https://www.samhsa.gov/find-help/harm-reduction"},
    {"term": "HALT", "definition": "An acronym (Hungry, Angry, Lonely, Tired) used in recovery to identify common triggers that can lead to relapse.",
     "source_name": "SMART Recovery", "source_url": "https://smartrecovery.org/"},
    {"term": "Hepatitis (Alcoholic)", "definition": "Inflammation of the liver caused by heavy alcohol consumption.",
     "source_name": "Mayo Clinic", "source_url": "https://www.mayoclinic.org/diseases-conditions/alcoholic-hepatitis/symptoms-causes/syc-20351388"},
    {"term": "Kindling", "definition": "A phenomenon in which repeated alcohol withdrawal episodes cause increasingly severe symptoms over time.",
     "source_name": "NIAAA — Alcohol Withdrawal", "source_url": "https://pubs.niaaa.nih.gov/publications/arh22-1/61-66.pdf"},
    {"term": "MCV (Mean Corpuscular Volume)", "definition": "Average size of red blood cells. Elevated MCV can be associated with chronic heavy alcohol use.",
     "source_name": "MedlinePlus (NIH)", "source_url": "https://medlineplus.gov/ency/article/003648.htm"},
    {"term": "Naltrexone", "definition": "A medication used to help reduce alcohol cravings and the rewarding effects of drinking. Always discuss with your doctor before starting.",
     "source_name": "NIAAA — Medications for AUD", "source_url": "https://www.niaaa.nih.gov/health-professionals-communities/core-resource-on-alcohol/medication-counseling-treatment"},
    {"term": "Protein (Dietary)", "definition": "An essential macronutrient that supports liver repair, muscle maintenance, and immune function. Recovery diets may emphasise higher protein intake — speak with your clinician for your target.",
     "source_name": "Australian Dietary Guidelines (NHMRC)", "source_url": "https://www.eatforhealth.gov.au/guidelines"},
    {"term": "Relapse", "definition": "A return to alcohol use after a period of abstinence. Often a part of the recovery journey, not a failure.",
     "source_name": "NIAAA — Treatment for AUD", "source_url": "https://www.niaaa.nih.gov/publications/brochures-and-fact-sheets/treatment-alcohol-problems-finding-and-getting-help"},
    {"term": "SMART Recovery", "definition": "Self-Management And Recovery Training: a science-based recovery program emphasizing self-empowerment and cognitive-behavioral techniques.",
     "source_name": "SMART Recovery", "source_url": "https://smartrecovery.org/"},
    {"term": "Sobriety", "definition": "The state of not being intoxicated; in recovery contexts, ongoing abstinence from alcohol.",
     "source_name": "NIAAA", "source_url": "https://www.niaaa.nih.gov/alcohols-effects-health/alcohol-use-disorder"},
    {"term": "Sodium / Salt", "definition": "An electrolyte important for fluid balance. Excess sodium can worsen high blood pressure and put strain on a recovering liver. 1g salt ≈ 400mg sodium. Australian and WHO guidance recommends <5g salt/day for general population; recovery diets may be stricter — speak with your clinician.",
     "source_name": "World Health Organization", "source_url": "https://www.who.int/news-room/fact-sheets/detail/salt-reduction"},
    {"term": "Sponsor", "definition": "In 12-step programs, an experienced member who guides a newer member through recovery.",
     "source_name": "Alcoholics Anonymous", "source_url": "https://www.aa.org/the-twelve-traditions"},
    {"term": "Thiamine (Vitamin B1)", "definition": "A vitamin commonly deficient in heavy drinkers. Supplementation helps prevent Wernicke-Korsakoff syndrome. Always consult your doctor for dosing.",
     "source_name": "NHS UK", "source_url": "https://www.nhs.uk/conditions/wernickes-encephalopathy/"},
    {"term": "Tolerance", "definition": "A reduced response to alcohol after repeated use, requiring more to achieve the same effect.",
     "source_name": "NIAAA", "source_url": "https://www.niaaa.nih.gov/alcohols-effects-health/alcohol-use-disorder"},
    {"term": "Trigger", "definition": "An emotional, environmental, or social situation that increases the urge to drink.",
     "source_name": "SMART Recovery", "source_url": "https://smartrecovery.org/"},
    {"term": "Water (Daily Intake)", "definition": "Adequate hydration matters in recovery. General adult guidance is roughly 2–2.5 L/day from all sources. Some recovery or medical contexts cap fluid intake — always follow your clinician's specific advice.",
     "source_name": "European Food Safety Authority", "source_url": "https://www.efsa.europa.eu/en/efsajournal/pub/1459"},
    {"term": "Wernicke-Korsakoff Syndrome", "definition": "A serious brain disorder caused by thiamine deficiency, commonly associated with chronic alcoholism.",
     "source_name": "NHS UK", "source_url": "https://www.nhs.uk/conditions/wernickes-encephalopathy/"},
    {"term": "Withdrawal", "definition": "Physical and psychological symptoms experienced when stopping alcohol use after dependency has formed. Can be medically serious — supervised detox may be required.",
     "source_name": "NIAAA — Alcohol Withdrawal", "source_url": "https://www.niaaa.nih.gov/publications/brochures-and-fact-sheets/treatment-alcohol-problems-finding-and-getting-help"},
]

# General references for the Sources page
GENERAL_SOURCES = [
    {"name": "National Institute on Alcohol Abuse and Alcoholism (NIAAA)", "url": "https://www.niaaa.nih.gov/", "purpose": "Primary source for alcohol use disorder definitions, withdrawal information, and treatment guidance."},
    {"name": "MedlinePlus (US National Library of Medicine)", "url": "https://medlineplus.gov/", "purpose": "Reference ranges and explanations of blood tests including ALT, AST, GGT, bilirubin, and MCV."},
    {"name": "SAMHSA (Substance Abuse and Mental Health Services Administration)", "url": "https://www.samhsa.gov/", "purpose": "Treatment referral, harm reduction, and crisis support information for the US."},
    {"name": "NHS UK", "url": "https://www.nhs.uk/", "purpose": "Patient-facing medical information on alcohol-related liver disease and Wernicke-Korsakoff syndrome."},
    {"name": "Mayo Clinic", "url": "https://www.mayoclinic.org/", "purpose": "Clinical reference for cirrhosis, alcoholic hepatitis, and dehydration."},
    {"name": "World Health Organization (WHO)", "url": "https://www.who.int/", "purpose": "Global guidance on salt reduction and population health."},
    {"name": "Australian Dietary Guidelines (NHMRC)", "url": "https://www.eatforhealth.gov.au/", "purpose": "Australian national dietary recommendations including protein intake."},
    {"name": "European Food Safety Authority (EFSA)", "url": "https://www.efsa.europa.eu/", "purpose": "Adequate intake values for water and other nutrients."},
    {"name": "Alcoholics Anonymous", "url": "https://www.aa.org/", "purpose": "12-step program information and meeting finder."},
    {"name": "SMART Recovery", "url": "https://smartrecovery.org/", "purpose": "Science-based peer recovery program."},
    {"name": "Samaritans (UK)", "url": "https://www.samaritans.org/", "purpose": "24/7 confidential crisis support in the UK."},
    {"name": "988 Suicide & Crisis Lifeline (US)", "url": "https://988lifeline.org/", "purpose": "24/7 crisis support in the US."},
    {"name": "Lifeline (Australia)", "url": "https://www.lifeline.org.au/", "purpose": "24/7 crisis support in Australia (13 11 14)."},
]

# Disclaimer text shown across the app
MEDICAL_DISCLAIMER = (
    "Anchor is a personal wellness journal. It is not a medical app and does not provide medical advice, "
    "diagnosis, or treatment. The dietary targets, glossary definitions, and document scanner are general "
    "wellness references drawn from public sources — not personalised health guidance. Always consult a "
    "qualified clinician about your personal health, medication, and diet. If you are in crisis, use the "
    "in-app Crisis page or call your local emergency number."
)
