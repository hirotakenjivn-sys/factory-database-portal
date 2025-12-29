import os

data = """CNC	DAY
ĐÓNG GÓI	DAY
HẠ NHIỆT	DAY
LÀM SẠCH SP	DAY
NHIỆT LUYỆN	DAY
NHUỘM ĐEN	DAY
QUAY BÓNG	DAY
RỬA	DAY
RỬA SẠCH DẦU	DAY
RUNG BAVIA	DAY
RUNG BÓNG	DAY
RUNG SẠCH	DAY
RUNG TẨY DẦU	DAY
RUNG TẨY TRẮNG	DAY
SƠN	DAY
 IN CHỮ	DAY
TẨY TRẮNG	DAY
XI MẠ	DAY
THỬ ỐC 100%	SPM
VÉT BAVIA LỖ	SPM
TÁN	SPM
XỬ LÝ BAVIA	SPM
XỬ LÝ CONG	SPM
XỬ LÝ MẶT PHẲNG	SPM
XỬ LÝ MÀI CẠNH	SPM
XỬ LÝ SẠCH SP	SPM
DẬP 1/1	SPM
DẬP 1/2	SPM
DẬP 2/2	SPM
DẬP 1/3	SPM
DẬP 2/3	SPM
DẬP 3/3	SPM
DẬP 1/4	SPM
DẬP 2/4	SPM
DẬP 3/4	SPM
DẬP 4/4	SPM
DẬP 1/5	SPM
DẬP 2/5	SPM
DẬP 3/5	SPM
DẬP 4/5	SPM
DẬP 5/5	SPM
DẬP 1/6	SPM
DẬP 2/6	SPM
DẬP 3/6	SPM
DẬP 4/6	SPM
DẬP 5/6	SPM
DẬP 6/6	SPM
DẬP 1/7	SPM
DẬP 2/7	SPM
DẬP 3/7	SPM
DẬP 4/7	SPM
DẬP 5/7	SPM
DẬP 6/7	SPM
DẬP 7/7	SPM
DẬP 1/8	SPM
DẬP 2/8	SPM
DẬP 3/8	SPM
DẬP 4/8	SPM
DẬP 5/8	SPM
DẬP 6/8	SPM
DẬP 7/8	SPM
DẬP 8/8	SPM
TARO 1/1	SPM
TARO 1/2	SPM
TARO 1/3	SPM
TARO 1/4	SPM
TARO 2/2	SPM
TARO 2/3	SPM
TARO 2/4	SPM
TARO 3/3	SPM
TARO 3/4	SPM
TARO 4/4	SPM"""

output_file = r"c:\Users\PCPV\factory-database-portal\database\import_process_names.sql"

sql_statements = []
sql_statements.append("USE factory_db;")
sql_statements.append("-- Import Process Names")
sql_statements.append("-- DAY = 0, SPM = 1")

for line in data.strip().split('\n'):
    if not line.strip():
        continue
    parts = line.split('\t')
    if len(parts) != 2:
        print(f"Skipping invalid line: {line}")
        continue
    
    name = parts[0].strip()
    type_str = parts[1].strip()
    
    # Map type to boolean (SPM=1, DAY=0)
    day_or_spm = 1 if type_str == 'SPM' else 0
    
    # Escape single quotes in name if any
    name_escaped = name.replace("'", "''")
    
    sql = f"INSERT INTO process_name_types (process_name, day_or_spm, user) VALUES ('{name_escaped}', {day_or_spm}, 'admin');"
    sql_statements.append(sql)

with open(output_file, 'w', encoding='utf-8') as f:
    f.write('\n'.join(sql_statements))

print(f"Generated {len(sql_statements) - 3} INSERT statements in {output_file}")
