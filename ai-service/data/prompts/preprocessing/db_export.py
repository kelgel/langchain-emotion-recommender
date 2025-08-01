import mysql.connector
from datetime import datetime
import sys

try:
    # DB 연결
    conn = mysql.connector.connect(
        host='tp4team5.cny6cmeagio6.ap-northeast-2.rds.amazonaws.com',
        user='admin',
        password='corzmdls1!',
        database='tp4team5'
    )

    cursor = conn.cursor()
    print("DB 연결 성공!")

    # 테이블 목록 가져오기
    cursor.execute("SHOW TABLES")
    tables = cursor.fetchall()
    print(f"총 {len(tables)}개 테이블 발견")

    # SQL 파일 생성
    with open('../../../../RDB/tp4team5_full_export.sql', 'w', encoding='utf-8') as f:
        f.write("-- tp4team5 데이터베이스 백업\n")
        f.write("-- 생성일: " + str(datetime.now()) + "\n\n")

        for (table,) in tables:
            print(f"테이블 {table} 처리 중...")

            # 테이블 구조
            cursor.execute(f"SHOW CREATE TABLE `{table}`")
            create_sql = cursor.fetchone()[1]
            f.write(f"-- 테이블 {table} 구조\n")
            f.write(f"DROP TABLE IF EXISTS `{table}`;\n")
            f.write(f"{create_sql};\n\n")

            # 데이터
            cursor.execute(f"SELECT * FROM `{table}`")
            rows = cursor.fetchall()

            if rows:
                f.write(f"-- 테이블 {table} 데이터\n")
                cursor.execute(f"DESCRIBE `{table}`")
                columns = [col[0] for col in cursor.fetchall()]

                for row in rows:
                    values = []
                    for val in row:
                        if val is None:
                            values.append('NULL')
                        elif isinstance(val, str):
                            # 문자열 이스케이프 처리
                            escaped_val = val.replace("'", "''")
                            values.append(f"'{escaped_val}'")
                        else:
                            values.append(f"'{str(val)}'")

                    # INSERT 문 생성 (루프 밖으로 이동)
                    columns_str = '`, `'.join(columns)
                    values_str = ', '.join(values)
                    f.write(f"INSERT INTO `{table}` (`{columns_str}`) VALUES ({values_str});\n")
                f.write("\n")

    print("✅ tp4team5_full_export.sql 파일 생성 완료!")

except Exception as e:
    print(f"❌ 오류 발생: {e}")
finally:
    if 'conn' in locals():
        conn.close()