#!/bin/bash
# サンプルデータ生成スクリプト
# 各テーブルに約200件のサンプルデータを生成します

OUTPUT_FILE="seed.sql"

cat > $OUTPUT_FILE << 'EOF'
-- Sample Data for Development/Testing (200 records per table)
-- Factory Database Portal

SET NAMES utf8mb4;

EOF

# ================================================
# Customers (顧客) - 200 records
# ================================================
echo "-- ================================================" >> $OUTPUT_FILE
echo "-- Customers (顧客) - 200 records" >> $OUTPUT_FILE
echo "-- ================================================" >> $OUTPUT_FILE
echo "INSERT INTO \`customers\` (\`customer_name\`, \`is_active\`, \`user\`) VALUES" >> $OUTPUT_FILE

COMPANIES=("トヨタ" "ホンダ" "日産" "マツダ" "スバル" "ダイハツ" "スズキ" "三菱" "いすゞ" "日野" "パナソニック" "ソニー" "東芝" "日立" "富士通" "NEC" "三菱電機" "シャープ" "キヤノン" "リコー")
SUFFIXES=("株式会社" "工業株式会社" "Co., Ltd." "Corporation" "Industries")

for i in $(seq 1 200); do
    COMPANY_IDX=$((i % 20))
    SUFFIX_IDX=$((i % 5))
    IS_ACTIVE=$((RANDOM % 10 > 0 ? 1 : 0))
    IS_ACTIVE_STR=$([[ $IS_ACTIVE -eq 1 ]] && echo "TRUE" || echo "FALSE")

    if [ $i -eq 200 ]; then
        echo "('${COMPANIES[$COMPANY_IDX]} ${SUFFIXES[$SUFFIX_IDX]} $(printf '%03d' $i)', $IS_ACTIVE_STR, 'admin');" >> $OUTPUT_FILE
    else
        echo "('${COMPANIES[$COMPANY_IDX]} ${SUFFIXES[$SUFFIX_IDX]} $(printf '%03d' $i)', $IS_ACTIVE_STR, 'admin')," >> $OUTPUT_FILE
    fi
done

echo "" >> $OUTPUT_FILE

# ================================================
# Products (製品) - 200 records
# ================================================
echo "-- ================================================" >> $OUTPUT_FILE
echo "-- Products (製品) - 200 records" >> $OUTPUT_FILE
echo "-- ================================================" >> $OUTPUT_FILE
echo "INSERT INTO \`products\` (\`product_code\`, \`customer_id\`, \`is_active\`, \`user\`) VALUES" >> $OUTPUT_FILE

PREFIXES=("TMC" "HMC" "NMC" "MMC" "SC" "DMC" "SMC" "IMC" "HMC" "TMC")

for i in $(seq 1 200); do
    PREFIX_IDX=$((i % 10))
    CUSTOMER_ID=$(((i % 200) + 1))
    IS_ACTIVE=$((RANDOM % 10 > 1 ? 1 : 0))
    IS_ACTIVE_STR=$([[ $IS_ACTIVE -eq 1 ]] && echo "TRUE" || echo "FALSE")

    if [ $i -eq 200 ]; then
        echo "('${PREFIXES[$PREFIX_IDX]}-$(printf '%04d' $i)', $CUSTOMER_ID, $IS_ACTIVE_STR, 'admin');" >> $OUTPUT_FILE
    else
        echo "('${PREFIXES[$PREFIX_IDX]}-$(printf '%04d' $i)', $CUSTOMER_ID, $IS_ACTIVE_STR, 'admin')," >> $OUTPUT_FILE
    fi
done

echo "" >> $OUTPUT_FILE

# ================================================
# Employees (従業員) - 200 records
# ================================================
echo "-- ================================================" >> $OUTPUT_FILE
echo "-- Employees (従業員) - 200 records" >> $OUTPUT_FILE
echo "-- ================================================" >> $OUTPUT_FILE
echo "INSERT INTO \`employees\` (\`employee_no\`, \`name\`, \`is_active\`, \`user\`) VALUES" >> $OUTPUT_FILE

LAST_NAMES=("佐藤" "鈴木" "高橋" "田中" "渡辺" "伊藤" "山本" "中村" "小林" "加藤" "吉田" "山田" "佐々木" "山口" "松本" "井上" "木村" "林" "斎藤" "清水")
FIRST_NAMES_MALE=("太郎" "次郎" "健一" "誠" "修" "勇" "聡" "隆" "浩" "和也")
FIRST_NAMES_FEMALE=("花子" "美咲" "愛" "優" "結衣" "陽菜" "美優" "莉子" "彩" "舞")

for i in $(seq 1 200); do
    LAST_IDX=$((i % 20))
    if [ $((i % 2)) -eq 0 ]; then
        FIRST_IDX=$((i % 10))
        NAME="${LAST_NAMES[$LAST_IDX]} ${FIRST_NAMES_MALE[$FIRST_IDX]}"
    else
        FIRST_IDX=$((i % 10))
        NAME="${LAST_NAMES[$LAST_IDX]} ${FIRST_NAMES_FEMALE[$FIRST_IDX]}"
    fi
    IS_ACTIVE=$((RANDOM % 20 > 0 ? 1 : 0))
    IS_ACTIVE_STR=$([[ $IS_ACTIVE -eq 1 ]] && echo "TRUE" || echo "FALSE")

    if [ $i -eq 200 ]; then
        echo "('EMP$(printf '%04d' $i)', '$NAME', $IS_ACTIVE_STR, 'admin');" >> $OUTPUT_FILE
    else
        echo "('EMP$(printf '%04d' $i)', '$NAME', $IS_ACTIVE_STR, 'admin')," >> $OUTPUT_FILE
    fi
done

echo "" >> $OUTPUT_FILE

# ================================================
# Suppliers (サプライヤー) - 200 records
# ================================================
echo "-- ================================================" >> $OUTPUT_FILE
echo "-- Suppliers (サプライヤー) - 200 records" >> $OUTPUT_FILE
echo "-- ================================================" >> $OUTPUT_FILE
echo "INSERT INTO \`suppliers\` (\`supplier_name\`, \`supplier_business\`, \`user\`) VALUES" >> $OUTPUT_FILE

SUPPLIER_SUFFIXES=("Manufacturing" "Industries" "Components" "Engineering" "Tech")
BUSINESSES=("Metal Processing" "Plastic Molding" "Surface Treatment" "Heat Treatment" "Machining" "Casting" "Forging" "Plating" "Coating" "Assembly")

for i in $(seq 1 200); do
    LETTER=$((65 + (i % 26)))
    LETTER_CHAR=$(printf "\\$(printf '%03o' "$LETTER")")
    SUFFIX_IDX=$((i % 5))
    BUSINESS_IDX=$((i % 10))

    if [ $i -eq 200 ]; then
        echo "('Supplier ${LETTER_CHAR}$(printf '%03d' $i) ${SUPPLIER_SUFFIXES[$SUFFIX_IDX]}', '${BUSINESSES[$BUSINESS_IDX]}', 'admin');" >> $OUTPUT_FILE
    else
        echo "('Supplier ${LETTER_CHAR}$(printf '%03d' $i) ${SUPPLIER_SUFFIXES[$SUFFIX_IDX]}', '${BUSINESSES[$BUSINESS_IDX]}', 'admin')," >> $OUTPUT_FILE
    fi
done

echo "" >> $OUTPUT_FILE

echo "データ生成完了！"
