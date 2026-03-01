import streamlit as st
import pandas as pd

# הגדרות דף
st.set_page_config(page_title="דירוג קרנות נאמנות", layout="wide")

# כותרות
st.title("🏆 מדרג קרנות הנאמנות מגן - Top 5")
st.markdown("המערכת מנתחת את הקובץ שלך ומציגה את הקרנות המנצחות לפי רמת סיכון וחשיפה למניות.")

# פונקציה לטעינה וניקוי נתונים
@st.cache_data
def load_data():
    try:
        df = pd.read_csv('mutual-funds.csv')
        
        # ניקוי עמודות מספריות
        cols_to_fix = ['תשואות 12 חודשים', 'דמי ניהול', 'סטיית תקן']
        for col in cols_to_fix:
            if col in df.columns:
                df[col] = pd.to_numeric(df[col].astype(str).str.replace('‎', '').replace('nan', '0').replace('%', ''), errors='coerce').fillna(0)
        
        # חישוב ציון משוקלל
        # נוסחה: (תשואה * 1.5) פחות (דמי ניהול * 15) פחות (סטיית תקן * 5)
        df['ציון סופי'] = (df['תשואות 12 חודשים'] * 1.5) - (df['דמי ניהול'] * 15) - (df['סטיית תקן'] * 5)
        
        # מיפוי קטגוריות חשיפה
        category_map = {
            0: "ללא מניות (0%)",
            1: "קרנות 10-90",
            2: "קרנות 20-80 / 30-70",
            3: "קרנות 40-60 / 50-50",
            4: "מניות (חשיפה גבוהה)",
            5: "מניות (חשיפה גבוהה)",
            6: "סיכון גבוה מאוד / ממונפות"
        }
        df['קטגוריה'] = df['פרופיל חשיפה מניות'].map(category_map)
        
        return df
    except Exception as e:
        st.error(f"שגיאה בטעינת הקובץ: {e}")
        return None

df = load_data()

if df is not None:
    # תפריט בחירה
    st.sidebar.header("הגדרות חיפוש")
    selected_cat = st.sidebar.selectbox(
        "בחר רמת חשיפה למניות:",
        ["הצג הכל", "ללא מניות (0%)", "קרנות 10-90", "קרנות 20-80 / 30-70", "קרנות 40-60 / 50-50", "מניות (חשיפה גבוהה)"]
    )

    # סינון נתונים
    if selected_cat == "הצג הכל":
        filtered_df = df
    else:
        filtered_df = df[df['קטגוריה'] == selected_cat]

    # הוצאת 5 המובילות
    top_5 = filtered_df.sort_values(by="ציון סופי", ascending=False).head(5)

    # תצוגה למשתמש
    st.subheader(f"📍 5 הקרנות המובילות בקטגוריה: {selected_cat}")
    
    if not top_5.empty:
        # עיצוב הטבלה
        st.dataframe(
            top_5[['שם הקרן', 'תשואות 12 חודשים', 'דמי ניהול', 'סטיית תקן', 'ציון סופי']],
            use_container_width=True,
            hide_index=True
        )
        
        # גרף השוואתי
        st.subheader("📊 השוואת תשואות מול דמי ניהול")
        st.bar_chart(top_5.set_index('שם הקרן')[['תשואות 12 חודשים', 'ציון סופי']])
    else:
        st.warning("לא נמצאו קרנות בקטגוריה זו בקובץ שהועלה.")

else:
    st.info("אנא וודא שהקובץ mutual-funds.csv נמצא באותה תיקייה עם הקוד.")

