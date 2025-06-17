# 🛠️ 기본 접속
psql -U jiwoo -d trials                          # 기본 DB 접속
psql -U jiwoo -d trials -h localhost             # 로컬 접속
\c trials                                        # 현재 세션에서 trials DB로 전환
\q                                               # psql 종료

# 📂 스키마 및 테이블 탐색 (ncbi, ctgov 중심)
\dn                                              # 스키마 목록 (ncbi, ctgov 확인)
\dt ncbi.*                                       # ncbi 스키마의 테이블 목록
\dt ctgov.*                                      # ctgov 스키마의 테이블 목록
\d ncbi.pm                                       # ncbi.pm 테이블 구조 확인
\d ctgov.study_references                        # ctgov.study_references 테이블 구조 확인
\d ctgov.studies                                 # ctgov.studies 테이블 구조 확인

# 특정 컬럼 가진 테이블 조회
SELECT table_schema, table_name, column_name
FROM information_schema.columns
WHERE column_name ILIKE '%pmid%';  #ILIKE 는 대소문자 구분 없이 검색

SELECT table_name, column_name
FROM information_schema.columns
WHERE column_name ILIKE '%result%'
  AND table_schema = 'ctgov';

# 🔍 조회 쿼리 예시 (자주 쓰는 패턴)
SELECT * FROM ncbi.pm WHERE pmid = '16897661';                     # pmid로 논문 조회
SELECT * FROM ctgov.study_references WHERE pmid = '16897661';     # pmid 기반 CTG 참조 검색
SELECT * FROM ctgov.studies WHERE nct_id = 'NCT00011011';         # nct_id로 study 검색
SELECT * FROM ctgov.studies WHERE nct_id IN ('NCT00099099','NCT00099151');  # 다중 NCT ID

# 🧠 조건 기반 JSONB 필터링 (review 논문 찾기)
SELECT * FROM ncbi.pm
WHERE jsonb_array_length(publication_types) >= 3
  AND EXISTS (
    SELECT 1 FROM jsonb_array_elements_text(publication_types) AS elem
    WHERE elem ILIKE '%review%'
  )
  AND jsonb_array_length(ref_nctids) >= 2
LIMIT 1;

# 🔗 PM ↔ CTG 참조 통합 조회 (pmid 기반)
WITH pm_refs AS (
  SELECT pm.pmid, jsonb_array_elements_text(pm.ref_nctids) AS nct_id,
         '-' AS reference_type, 'pm' AS source
  FROM ncbi.pm pm
  WHERE pm.pmid = '16897661' AND pm.ref_nctids IS NOT NULL
),
ctg_refs AS (
  SELECT ctg_ref.pmid, ctg_ref.nct_id, ctg_ref.reference_type, 'ctg' AS source
  FROM ctgov.study_references ctg_ref
  WHERE ctg_ref.pmid = '16897661'
),
combined_refs AS (
  SELECT * FROM ctg_refs
  UNION ALL
  SELECT * FROM pm_refs
),
deduped_refs AS (
  SELECT DISTINCT ON (pmid, nct_id)
    nct_id, pmid, reference_type, source
  FROM combined_refs
  ORDER BY pmid, nct_id, CASE source WHEN 'ctg' THEN 0 ELSE 1 END
)
SELECT ref.nct_id AS nctid, ref.pmid, ref.reference_type,
       ctg_study.brief_title, ctg_study.official_title, ctg_study.overall_status
FROM deduped_refs ref
LEFT JOIN ctgov.studies ctg_study ON ctg_study.nct_id = ref.nct_id;

# 🗃️ 파일 입출력
\i query.sql                                     # SQL 파일 실행
\copy ncbi.pm TO 'pm.csv' CSV HEADER;            # 테이블 → CSV 저장
\copy ncbi.pm FROM 'pm.csv' CSV HEADER;          # CSV → 테이블 불러오기

# 🧭 기타 유용한 도구
\conninfo                                        # 현재 접속 정보 확인
\set AUTOCOMMIT off                              # 자동 커밋 끄기
\pset pager off                                  # 페이지 나눔 비활성화
\watch 2 SELECT count(*) FROM ncbi.pm;           # 실시간 모니터링 (2초마다)

# 🧪 1. PMID 단건 및 다건 조회
SELECT * FROM ncbi.pm WHERE pmid = '16897661';
SELECT * FROM ncbi.pm WHERE pmid IN ('31906264', '32873434');

# 🔗 2. PMID ↔ NCT ID 기반 양방향 참조 조회
-- CTG 참조 테이블 기준
SELECT * FROM ctgov.study_references WHERE pmid = '16897661';
-- NCT ID → study 정보
SELECT * FROM ctgov.studies WHERE nct_id = 'NCT00011011';
-- NCT ID 여러 개
SELECT * FROM ctgov.studies WHERE nct_id IN ('NCT00099099', 'NCT00099151');

# 🧠 3. review 논문 필터 (publication_types에 review 포함 & ref_nctids 길이 ≥ 2)
SELECT * FROM ncbi.pm
WHERE jsonb_array_length(publication_types) >= 3
  AND EXISTS (
    SELECT 1 FROM jsonb_array_elements_text(publication_types) elem
    WHERE elem ILIKE '%review%'
  )
  AND jsonb_array_length(ref_nctids) >= 2;

# 🔎 4. ref_nctids 배열에 NCT ID 포함된 논문 찾기
SELECT pmid FROM ncbi.pm
WHERE ref_nctids ? 'NCT00011011';

# 🔁 5. pmid로 CTG-study 정보까지 매핑된 종합 쿼리 (dedup + join)
WITH pm_refs AS (
  SELECT pm.pmid, jsonb_array_elements_text(pm.ref_nctids) AS nct_id,
         '-' AS reference_type, 'pm' AS source
  FROM ncbi.pm pm
  WHERE pm.ref_nctids IS NOT NULL AND pm.pmid = '16897661'
),
ctg_refs AS (
  SELECT pmid, nct_id, reference_type, 'ctg' AS source
  FROM ctgov.study_references
  WHERE pmid = '16897661'
),
combined_refs AS (
  SELECT * FROM pm_refs
  UNION ALL
  SELECT * FROM ctg_refs
),
deduped_refs AS (
  SELECT DISTINCT ON (pmid, nct_id)
         nct_id, pmid, reference_type, source
  FROM combined_refs
  ORDER BY pmid, nct_id, CASE source WHEN 'ctg' THEN 0 ELSE 1 END
)
SELECT 
  ref.nct_id AS nctid, ref.pmid, ref.reference_type, ref.source,
  s.brief_title, s.overall_status
FROM deduped_refs ref
LEFT JOIN ctgov.studies s ON ref.nct_id = s.nct_id;

# 📚 6. publication_year 추출 및 연도별 논문 수 집계
SELECT
  pmid,
  (xpath('//PubDate/Year/text()', pubdate_xml))[1]::text::int AS pub_year
FROM ncbi.pm
WHERE pubdate_xml IS NOT NULL
LIMIT 10;

SELECT
  (xpath('//PubDate/Year/text()', pubdate_xml))[1]::text::int AS pub_year,
  COUNT(*) as num_pubs
FROM ncbi.pm
WHERE pubdate_xml IS NOT NULL
GROUP BY pub_year
ORDER BY pub_year DESC;

SELECT 
  EXTRACT(YEAR FROM publication_date) AS year,
  COUNT(DISTINCT publication_date) AS count
FROM ncbi.pm
GROUP BY year
ORDER BY year DESC;


# 🧩 7. 특정 키워드 포함 논문 검색 (MeSH terms 또는 title/abstract 기반)
SELECT * FROM ncbi.pm
WHERE abstract ILIKE '%randomized%' OR title ILIKE '%randomized%';

# 📌 8. 특정 조건 만족하는 CTG study 목록 (예: status = Completed, 최근 등록)
SELECT * FROM ctgov.studies
WHERE overall_status = 'Completed'
ORDER BY start_date DESC
LIMIT 20;

# 🔬 9. PMID 기준으로 매핑된 모든 NCT ID 리스트 (jsonb → text 배열로)
SELECT pmid, jsonb_array_elements_text(ref_nctids) AS nct_id
FROM ncbi.pm
WHERE pmid = '16897661';

# 📄 10. publication_types 종류별 개수 통계
SELECT elem AS type, COUNT(*) FROM (
  SELECT jsonb_array_elements_text(publication_types) AS elem
  FROM ncbi.pm
) t
GROUP BY elem
ORDER BY COUNT(*) DESC;

# 🧹 11. ref_nctids가 NULL이 아닌 논문 수 + 평균 연결 NCT 수
SELECT COUNT(*) AS num_pmids_with_refs,
       AVG(jsonb_array_length(ref_nctids)) AS avg_linked_trials
FROM ncbi.pm
WHERE ref_nctids IS NOT NULL;
