/**
 * 日付フォーマット用ユーティリティ関数
 * ベトナムの標準フォーマット DD/MM/YYYY に統一
 */

/**
 * YYYY-MM-DD形式の文字列をDD/MM/YYYY形式に変換
 * @param {string} dateString - YYYY-MM-DD形式の日付文字列
 * @returns {string} DD/MM/YYYY形式の日付文字列
 */
export function formatDateForDisplay(dateString) {
  if (!dateString) return ''

  try {
    // YYYY-MM-DD形式をパース
    const parts = dateString.split('-')
    if (parts.length === 3) {
      const [year, month, day] = parts
      return `${day}/${month}/${year}`
    }

    // すでにDD/MM/YYYY形式の場合はそのまま返す
    if (dateString.includes('/')) {
      return dateString
    }

    return dateString
  } catch (error) {
    console.error('Date format error:', error)
    return dateString
  }
}

/**
 * DD/MM/YYYY形式の文字列をYYYY-MM-DD形式に変換（API送信用）
 * @param {string} dateString - DD/MM/YYYY形式の日付文字列
 * @returns {string} YYYY-MM-DD形式の日付文字列
 */
export function formatDateForApi(dateString) {
  if (!dateString) return ''

  try {
    // DD/MM/YYYY形式をパース
    const parts = dateString.split('/')
    if (parts.length === 3) {
      const [day, month, year] = parts
      return `${year}-${month.padStart(2, '0')}-${day.padStart(2, '0')}`
    }

    // すでにYYYY-MM-DD形式の場合はそのまま返す
    if (dateString.includes('-')) {
      return dateString
    }

    return dateString
  } catch (error) {
    console.error('Date format error:', error)
    return dateString
  }
}

/**
 * 今日の日付をDD/MM/YYYY形式で取得
 * @returns {string} DD/MM/YYYY形式の今日の日付
 */
export function getTodayFormatted() {
  const today = new Date()
  const day = String(today.getDate()).padStart(2, '0')
  const month = String(today.getMonth() + 1).padStart(2, '0')
  const year = today.getFullYear()
  return `${day}/${month}/${year}`
}

/**
 * Date オブジェクトをDD/MM/YYYY形式に変換
 * @param {Date} date - Dateオブジェクト
 * @returns {string} DD/MM/YYYY形式の日付文字列
 */
export function formatDate(date) {
  if (!date) return ''

  try {
    if (!(date instanceof Date)) {
      date = new Date(date)
    }

    const day = String(date.getDate()).padStart(2, '0')
    const month = String(date.getMonth() + 1).padStart(2, '0')
    const year = date.getFullYear()
    return `${day}/${month}/${year}`
  } catch (error) {
    console.error('Date format error:', error)
    return ''
  }
}

/**
 * DD/MM/YYYY形式の文字列をDateオブジェクトに変換
 * @param {string} dateString - DD/MM/YYYY形式の日付文字列
 * @returns {Date} Dateオブジェクト
 */
export function parseDate(dateString) {
  if (!dateString) return null

  try {
    const parts = dateString.split('/')
    if (parts.length === 3) {
      const [day, month, year] = parts
      return new Date(year, month - 1, day)
    }

    return new Date(dateString)
  } catch (error) {
    console.error('Date parse error:', error)
    return null
  }
}
