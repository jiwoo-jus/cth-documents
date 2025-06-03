import os
import re
import requests
import json
import time
from itertools import zip_longest

# ------------------- Output File Paths -------------------
CTG_PATH = "./SAMPLE/CTG"
PM_PATH = "./SAMPLE/PM"
PMC_PATH = "./SAMPLE/PMC"
MEDLINE_PATH = "./SAMPLE/MEDLINE"  # 새로운 MEDLINE 디렉토리 추가

# ------------------- Input File Paths -------------------
TARGET_SAMPLES = "/users/PAS2836/jiwjus/ClinicalTrialsHub/SAMPLE_MCMASTER/sampleids_mcmaster.txt"

# ------------------- Configuration Options -------------------
find_flag = "DIRECT"  # "CASE" or "DIRECT"

CASE_NUMBERS = [
    1, 2, 3, 4, 5, 6, 7, 8, 9, 10
]  # CASE 모드에서 처리할 케이스 번호

DIRECT_NCTID = []  # DIRECT 모드에서 처리할 NCTID
DIRECT_PMID = ['28496314']  # DIRECT 모드에서 처리할 PMID
DIRECT_PMCID = []  # DIRECT 모드에서 처리할 PMCID

FETCH_CTG = False  # Set to False to skip ClinicalTrials.gov data
FETCH_PM = True  # Set to False to skip PubMed data
FETCH_PMC = False  # Set to False to skip PubMed Central data
FETCH_MEDLINE = True  # Set to False to skip MEDLINE data
FIELD_GROUP_KEY = "group0"  # group0: all
FIELD_GROUP = {
    "group0": "protocolSection,resultsSection,annotationSection,documentSection,derivedSection,hasResults",
    "group1": "protocolSection.identificationModule,protocolSection.oversightModule,protocolSection.descriptionModule,"
              "protocolSection.conditionsModule,protocolSection.designModule,protocolSection.armsInterventionsModule,"
              "protocolSection.outcomesModule,protocolSection.eligibilityModule,protocolSection.ipdSharingStatementModule,"
              "ResultsSection",
    "group2": "protocolSection",
    "group3": "ResultsSection",
    "group4": "protocolSection.identificationModule.nctId,protocolSection.identificationModule.orgStudyIdInfo.id,"
              "protocolSection.identificationModule.orgStudyIdInfo.type,protocolSection.identificationModule.orgStudyIdInfo.link,"
              "protocolSection.identificationModule.secondaryIdInfos.id,protocolSection.identificationModule.secondaryIdInfos.type,"
              "protocolSection.identificationModule.secondaryIdInfos.domain,protocolSection.identificationModule.secondaryIdInfos.link,"
              "protocolSection.identificationModule.briefTitle,protocolSection.identificationModule.officialTitle,"
              "protocolSection.identificationModule.acronym,protocolSection.identificationModule.organization.fullName,"
              "protocolSection.identificationModule.organization.class,protocolSection.descriptionModule.briefSummary,"
              "protocolSection.descriptionModule.detailedDescription,protocolSection.conditionsModule.conditions,"
              "protocolSection.conditionsModule.keywords,protocolSection.designModule.studyType,"
              "protocolSection.designModule.patientRegistry,protocolSection.designModule.targetDuration,"
              "protocolSection.designModule.phases,protocolSection.designModule.designInfo.allocation,"
              "protocolSection.designModule.designInfo.interventionModel,protocolSection.designModule.designInfo.interventionModelDescription,"
              "protocolSection.designModule.designInfo.primaryPurpose,protocolSection.designModule.designInfo.observationalModel,"
              "protocolSection.designModule.designInfo.timePerspective,protocolSection.designModule.designInfo.maskingInfo.masking,"
              "protocolSection.designModule.designInfo.maskingInfo.maskingDescription,protocolSection.designModule.designInfo.maskingInfo.whoMasked,"
              "protocolSection.designModule.enrollmentInfo.count,protocolSection.designModule.enrollmentInfo.type,"
              "protocolSection.armsInterventionsModule.armGroups.label,protocolSection.armsInterventionsModule.armGroups.type,"
              "protocolSection.armsInterventionsModule.armGroups.description,protocolSection.armsInterventionsModule.armGroups.interventionNames,"
              "protocolSection.armsInterventionsModule.interventions.type,protocolSection.armsInterventionsModule.interventions.name,"
              "protocolSection.armsInterventionsModule.interventions.description,protocolSection.armsInterventionsModule.interventions.armGroupLabels,"
              "protocolSection.outcomesModule.primaryOutcomes.measure,protocolSection.outcomesModule.primaryOutcomes.description,"
              "protocolSection.outcomesModule.primaryOutcomes.timeFrame,protocolSection.outcomesModule.secondaryOutcomes.measure,"
              "protocolSection.outcomesModule.secondaryOutcomes.description,protocolSection.outcomesModule.secondaryOutcomes.timeFrame,"
              "protocolSection.outcomesModule.otherOutcomes.measure,protocolSection.outcomesModule.otherOutcomes.description,"
              "protocolSection.outcomesModule.otherOutcomes.timeFrame,protocolSection.eligibilityModule.eligibilityCriteria,"
              "protocolSection.eligibilityModule.healthyVolunteers,protocolSection.eligibilityModule.sex,"
              "protocolSection.eligibilityModule.minimumAge,protocolSection.eligibilityModule.maximumAge,"
              "protocolSection.eligibilityModule.stdAges,protocolSection.eligibilityModule.studyPopulation,"
              "protocolSection.eligibilityModule.samplingMethod"
}

# ------------------- Ensure directories exist -------------------
os.makedirs(CTG_PATH, exist_ok=True)
os.makedirs(PM_PATH, exist_ok=True)
os.makedirs(PMC_PATH, exist_ok=True)
os.makedirs(MEDLINE_PATH, exist_ok=True)  # MEDLINE 디렉토리 생성


# Save data to a file
def save_to_file(data, file_path):
    try:
        with open(file_path, 'w', encoding='utf-8') as f:
            if file_path.endswith('.json'):
                json.dump(data, f, ensure_ascii=False, indent=4)
            else:
                f.write(data)
        print(f"Data saved to {file_path}")
    except Exception as e:
        print(f"Error saving data to file: {e}")


# Fetch ClinicalTrials.gov data
def fetch_ctg(nctid, caseno):
    url = f"https://clinicaltrials.gov/api/v2/studies/{nctid}"
    params = {"fields": FIELD_GROUP.get(FIELD_GROUP_KEY)}

    response = requests.get(url, params=params)
    if response.status_code == 200:
        file_path = os.path.join(CTG_PATH, f"case{caseno}_ctg_{FIELD_GROUP_KEY}.json")
        save_to_file(response.json(), file_path)
    else:
        print(f"Error fetching CTG data for {nctid}: {response.status_code}")


# Fetch PubMed data
def fetch_pm(pmid, caseno):
    url = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/efetch.fcgi"
    params = {"db": "pubmed", "id": pmid, "retmode": "xml"}

    response = requests.get(url, params=params)
    if response.status_code == 200:
        file_path = os.path.join(PM_PATH, f"case{caseno}_pm.xml")
        save_to_file(response.text, file_path)
    else:
        print(f"Error fetching PubMed data for {pmid}: {response.status_code}")


# Fetch PubMed Central data
def fetch_pmc(pmcid, caseno):
    url = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/efetch.fcgi"
    params = {"db": "pmc", "id": pmcid, "retmode": "xml"}

    response = requests.get(url, params=params)
    if response.status_code == 200:
        file_path = os.path.join(PMC_PATH, f"case{caseno}_pmc.xml")
        save_to_file(response.text, file_path)
    else:
        print(f"Error fetching PMC data for {pmcid}: {response.status_code}")


# Fetch MEDLINE data
def fetch_medline(pmid, caseno):
    url = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/efetch.fcgi"
    params = {
        "db": "pubmed", 
        "id": pmid, 
        "retmode": "text", 
        "rettype": "medline"  # MEDLINE 형식으로 요청
    }

    response = requests.get(url, params=params)
    if response.status_code == 200:
        file_path = os.path.join(MEDLINE_PATH, f"case{caseno}_medline.txt")
        save_to_file(response.text, file_path)
    else:
        print(f"Error fetching MEDLINE data for {pmid}: {response.status_code}")


# Extract metadata from the input file
def extract_metadata():
    if not os.path.exists(TARGET_SAMPLES):
        raise FileNotFoundError(f"Input file not found: {TARGET_SAMPLES}")

    with open(TARGET_SAMPLES, 'r', encoding='utf-8') as file:
        content = file.readlines()

    # [0] NCTID: NCT02229851, PMID: 39991735, PMCID: 11842232
    pattern = re.compile(r'\[(\d+)\]\s*NCTID:\s*(NCT\d+),\s*PMID:\s*(\d+),\s*PMCID:\s*(\d+)')
    extracted_data = []

    for line in content:
        match = pattern.search(line)
        if match:
            caseno = int(match.group(1))
            if CASE_NUMBERS and caseno not in CASE_NUMBERS:
                continue  # Process only selected case numbers if specified

            metadata = {
                "caseno": caseno,
                "nctid": match.group(2),
                "pmid": match.group(3),
                "pmcid": match.group(4),
            }
            extracted_data.append(metadata)

    return extracted_data


if __name__ == "__main__":
    if find_flag == "CASE":
        cases = extract_metadata()
        print("hi")
    elif find_flag == "DIRECT":
        cases = [
            {"nctid": nctid, "pmid": pmid, "pmcid": pmcid}
        for nctid, pmid, pmcid in zip_longest(DIRECT_NCTID, DIRECT_PMID, DIRECT_PMCID, fillvalue=None)
        ]
        print("DIRECT SAMPLES: ", cases)
    else:
        raise ValueError("Invalid find_flag value. Use 'CASE' or 'DIRECT'.")

    for case in cases:
        time.sleep(3)  # Delay between API requests
        print("Processing case:", case)
        
        if FETCH_CTG and case.get("nctid"):
            nctid = case["nctid"]
            fetch_ctg(nctid, case.get("caseno", "direct"))

        if FETCH_PM and case.get("pmid"):
            pmid = case["pmid"]
            fetch_pm(pmid, case.get("caseno", "direct"))

        if FETCH_PMC and case.get("pmcid"):
            pmcid = case["pmcid"]
            fetch_pmc(pmcid, case.get("caseno", "direct"))
            
        if FETCH_MEDLINE and case.get("pmid"):
            pmid = case["pmid"]
            fetch_medline(pmid, case.get("caseno", "direct"))