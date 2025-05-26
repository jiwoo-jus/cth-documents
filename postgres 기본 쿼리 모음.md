## 📂 터미널(Shell) 명령어

```bash
# 데이터베이스 생성
createdb mydb

# 데이터베이스 삭제
dropdb mydb

# 데이터베이스 접속
psql -d mydb

# 특정 유저로 접속
psql -U postgres -d mydb

# 특정 호스트에서 접속
psql -h localhost -U postgres -d mydb

# SQL 파일 실행
psql -d mydb -f script.sql

# 백업 (덤프)
pg_dump mydb > backup.sql

# 복원
psql -d mydb < backup.sql
```

---

## 🖥️ psql 접속 후 명령어

### 1. 연결 및 환경

```sql
# 다른 데이터베이스로 접속
\c otherdb

# 현재 접속된 데이터베이스 확인
SELECT current_database();

# 현재 유저 확인
SELECT current_user;

# 현재 서버 시간
SELECT now();

# 접속 종료
\q
```

---

### 2. 데이터베이스 / 스키마 / 테이블 구조 확인

```sql
# 모든 데이터베이스 목록
\l

# 현재 데이터베이스의 모든 테이블
\dt

# 현재 데이터베이스의 모든 스키마
\dn

# 현재 데이터베이스의 모든 관계형 객체 (뷰 등 포함)
\d

# 특정 테이블의 컬럼 및 정보 확인
\d tablename

# 현재 스키마 확인
SHOW search_path;

# 스키마 설정
SET search_path TO myschema;
```

---

### 3. 테이블 관리

```sql
# 테이블 생성
CREATE TABLE users (
  id SERIAL PRIMARY KEY,
  name TEXT,
  email TEXT UNIQUE
);

# 테이블 삭제
DROP TABLE users;

# 테이블 이름 변경
ALTER TABLE users RENAME TO members;

# 컬럼 추가
ALTER TABLE users ADD COLUMN age INT;

# 컬럼 삭제
ALTER TABLE users DROP COLUMN age;

# 컬럼 이름 변경
ALTER TABLE users RENAME COLUMN name TO full_name;

# 데이터 전체 삭제 (구조는 유지)
TRUNCATE TABLE users;
```

---

### 4. 스키마 관리

```sql
# 스키마 생성
CREATE SCHEMA analytics;

# 스키마 삭제
DROP SCHEMA analytics;

# 스키마 이름 변경
ALTER SCHEMA analytics RENAME TO insights;
```

---

### 5. 데이터 조작 (DML)

```sql
# 데이터 삽입
INSERT INTO users (name, email) VALUES ('Alice', 'alice@example.com');

# 데이터 조회
SELECT * FROM users;

# 조건부 조회
SELECT * FROM users WHERE id = 1;

# 정렬
SELECT * FROM users ORDER BY id DESC;

# 수정
UPDATE users SET name = 'Bob' WHERE id = 1;

# 삭제
DELETE FROM users WHERE id = 1;

# 레코드 수 세기
SELECT COUNT(*) FROM users;
```

---

### 6. 사용자 및 권한 관리 (기본)

```sql
# 유저 생성
CREATE USER myuser WITH PASSWORD 'mypass';

# 유저 삭제
DROP USER myuser;

# 권한 부여
GRANT ALL PRIVILEGES ON DATABASE mydb TO myuser;

# 권한 회수
REVOKE ALL PRIVILEGES ON DATABASE mydb FROM myuser;
```

---

### 7. 테이블에 있는 행 개수 조회

```sql
# 특정 테이블의 총 행 개수
SELECT COUNT(*) FROM tablename;
```

---

### 8. 특정 컬럼명을 가진 테이블 찾기 (INFORMATION\_SCHEMA)

기본 구조는 다음과 같아:

```sql
SELECT table_schema, table_name, column_name
FROM information_schema.columns
WHERE column_name ILIKE '패턴';
```

#### 정확히 일치하는 컬럼명 찾기

```sql
-- 정확히 'email'이라는 컬럼이 있는 테이블 찾기
SELECT table_name
FROM information_schema.columns
WHERE column_name = 'email';
```

#### 특정 단어를 포함하는 컬럼 찾기

```sql
-- 'date'를 포함하는 컬럼
SELECT table_name, column_name
FROM information_schema.columns
WHERE column_name ILIKE '%date%';
```

#### 특정 스키마에만 제한 (예: public)

```sql
-- public 스키마에서 'status'를 포함하는 컬럼
SELECT table_name, column_name
FROM information_schema.columns
WHERE table_schema = 'public'
  AND column_name ILIKE '%status%';
```

#### `DISTINCT table_name`으로 중복 없이 테이블 이름만 출력할 수도 있어:

```sql
SELECT DISTINCT table_name
FROM information_schema.columns
WHERE column_name ILIKE '%email%';
```
