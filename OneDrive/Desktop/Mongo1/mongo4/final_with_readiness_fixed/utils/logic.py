import pandas as pd
import numpy as np

MEDICAL_SCORE = {
    'A1': 100, 'A2': 95,
    'B1': 88,  'B2': 82,
    'C1': 75,  'C2': 68,
}
READINESS_SCORE = {'High': 3, 'Medium': 2, 'Low': 1}
LEADERSHIP_MAP = {'High': 3, 'Medium': 2, 'Low': 1, 'Yes': 3, 'No': 1}
ATTRITION_RISK_MAP = {'High': 3, 'Medium': 2, 'Low': 1}

def load_df(csv_path: str) -> pd.DataFrame:
    df = pd.read_csv(csv_path)
    for col in ["Last_Medical_Checkup", "Last_Mission_Date"]:
        if col in df.columns:
            df[col] = pd.to_datetime(df[col], errors='coerce')
    return df

def add_derived_columns(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    df["Medical_Score"] = df["Medical_Category"].map(MEDICAL_SCORE).fillna(60)
    df["Leadership_Score"] = df["Leadership_Potential"].map(LEADERSHIP_MAP).fillna(1)
    df["Readiness_Score"] = df["Readiness_Level"].map(READINESS_SCORE).fillna(1)
    if "Attrition_Risk" in df.columns:
        df["Attrition_Score"] = df["Attrition_Risk"].map(ATTRITION_RISK_MAP).fillna(2)
    else:
        df["Attrition_Score"] = 2
    return df

def who_is_going_to_leave(df: pd.DataFrame, top_n: int = 50) -> pd.DataFrame:
    d = add_derived_columns(df)
    if "Attrition_Risk" in d.columns:
        out = d.sort_values(["Attrition_Score", "Years_of_Service"], ascending=[False, True])
        return out[["Personnel_ID", "Name", "Rank", "Years_of_Service", "Attrition_Risk", "Performance_Rating"]].head(top_n)
    score = (
        (d["Years_of_Service"].fillna(0) > 20).astype(int)
        + (d["Performance_Rating"].fillna(3) <= 2).astype(int)
        + (d["Training_Score"].fillna(60) < 50).astype(int)
    )
    d["Heuristic_Attrition"] = np.where(score >= 2, "High", np.where(score==1, "Medium", "Low"))
    out = d.sort_values(["Heuristic_Attrition", "Years_of_Service"], ascending=[False, True])
    return out[["Personnel_ID", "Name", "Rank", "Years_of_Service", "Heuristic_Attrition", "Performance_Rating"]].head(top_n)

def medical_scores(df: pd.DataFrame) -> pd.DataFrame:
    d = add_derived_columns(df)
    return d[["Personnel_ID", "Name", "Rank", "Medical_Category", "Medical_Score", "BMI", "Last_Medical_Checkup"]]

def who_needs_training(df: pd.DataFrame, thresh: int = 60) -> pd.DataFrame:
    d = add_derived_columns(df)
    need = d[d["Training_Score"].fillna(0) < thresh]
    return need[["Personnel_ID", "Name", "Rank", "Training_Course", "Training_Score", "Performance_Rating"]].sort_values("Training_Score")

def leadership_list(df: pd.DataFrame) -> pd.DataFrame:
    d = add_derived_columns(df)
    cols = ["Personnel_ID","Name","Rank","Primary_Skill",
            "Leadership_Potential","Performance_Rating","Missions_Completed"]
    cols = [c for c in cols if c in d.columns]
    return d.sort_values(["Leadership_Score", "Performance_Rating"], ascending=[False, False])[cols]


def skill_grouping(df: pd.DataFrame) -> dict:
    groups = {}
    if "Primary_Skill" in df.columns:
        for skill, g in df.groupby("Primary_Skill"):
            groups[skill] = g[["Personnel_ID", "Name", "Rank", "Performance_Rating", "Readiness_Level", "Medical_Category"]].to_dict(orient="records")
    return groups

def select_best_team(df: pd.DataFrame, headcount: int, required_roles=None, restrict_to_roles: bool = False) -> pd.DataFrame:
    """
    Build a team ranked by an 'Overall' score.
    - required_roles: list of Primary_Skill values to prioritize or restrict to
    - restrict_to_roles=True means pick ONLY from those roles (fixes 'any skill shows same data')
    """

    d = add_derived_columns(df).copy()

    # Safe numeric casts
    for col in ["Performance_Rating", "Training_Score", "Missions_Completed"]:
        if col in d.columns:
            d[col] = pd.to_numeric(d[col], errors="coerce").fillna(0)
        else:
            d[col] = 0

    # Derive mapped scores if not already present
    if "Medical_Score" not in d.columns and "Medical_Category" in d.columns:
        d["Medical_Score"] = d["Medical_Category"].map(MEDICAL_SCORE).fillna(0)
    if "Readiness_Score" not in d.columns and "Readiness_Level" in d.columns:
        d["Readiness_Score"] = d["Readiness_Level"].map(READINESS_SCORE).fillna(0)
    if "Leadership_Score" not in d.columns and "Leadership_Potential" in d.columns:
        d["Leadership_Score"] = d["Leadership_Potential"].map(LEADERSHIP_MAP).fillna(0)

    # Normalize some pieces
    denom_missions = float(max(d["Missions_Completed"].max(), 1))
    perf_norm      = d["Performance_Rating"] / (5.0 if d["Performance_Rating"].max() <= 5 else max(d["Performance_Rating"].max(), 1))
    train_norm     = d["Training_Score"] / 100.0
    medical_norm   = d["Medical_Score"] / 100.0

    # Weighted Overall score (tweakable weights)
    d["Overall"] = (
        2.5 * d["Readiness_Score"] +
        1.5 * d["Leadership_Score"] +
        1.2 * perf_norm +
        1.0 * medical_norm +
        0.6 * train_norm +
        0.4 * (d["Missions_Completed"] / denom_missions)
    )

    # If restricting, keep only the requested skills
    if restrict_to_roles and required_roles:
        d = d[d["Primary_Skill"].isin(required_roles)]

    # If not restricting, make sure we at least take one per requested role (when provided)
    picked_idx = []
    if required_roles and not restrict_to_roles:
        for role in required_roles:
            sub = d[d["Primary_Skill"] == role]
            if len(sub):
                picked_idx.append(sub.sort_values("Overall", ascending=False).index[0])

    # Fill any remaining slots purely by best Overall
    remaining = headcount - len(picked_idx)
    rest = d.drop(index=picked_idx).sort_values("Overall", ascending=False).head(max(0, remaining))
    team = pd.concat([d.loc[picked_idx], rest]).sort_values("Overall", ascending=False).head(headcount)

    cols = ["Personnel_ID","Name","Rank","Primary_Skill","Readiness_Level","Medical_Category",
            "Leadership_Potential","Performance_Rating","Overall"]
    # Only keep columns that exist
    cols = [c for c in cols if c in team.columns] + ["Overall"]
    cols = list(dict.fromkeys(cols))  # de-dupe while keeping order
    return team[cols]

def what_if_simulation(df: pd.DataFrame, text: str) -> dict:
    """
    Enhanced NLP-powered what-if scenario analysis
    Handles complex queries about retiring officers, redeploying staff, grounding pilots, etc.
    """
    import re
    import os
    
    text_low = text.lower()
    result = {"query": text, "analysis": "", "recommendations": [], "data": []}
    
    # Initialize OpenAI client if API key is available
    client = None
    try:
        from openai import OpenAI
        api_key = os.environ.get("OPENAI_API_KEY")
        if api_key and api_key != "your_openai_api_key_here":
            client = OpenAI(api_key=api_key)
    except ImportError:
        # OpenAI not installed, continue without it
        client = None
    except Exception:
        client = None
    
    # Enhanced keyword-based analysis for complex scenarios
    if any(word in text_low for word in ["retire", "retiring", "retirement"]):
        result.update(_analyze_retirement_scenario(df, text_low, client))
    elif any(word in text_low for word in ["redeploy", "redeployment", "transfer", "move"]):
        result.update(_analyze_redeployment_scenario(df, text_low, client))
    elif any(word in text_low for word in ["ground", "grounding", "medical", "unfit", "disqualify"]):
        result.update(_analyze_grounding_scenario(df, text_low, client))
    elif any(word in text_low for word in ["promote", "promotion", "advance"]):
        result.update(_analyze_promotion_scenario(df, text_low, client))
    elif any(word in text_low for word in ["budget", "cost", "financial", "expense"]):
        result.update(_analyze_budget_scenario(df, text_low, client))
    elif "training" in text_low and any(tok in text_low for tok in ["threshold", "score", "<", "less than", "below"]):
        m = re.search(r"(\d{2})", text_low)
        thresh = int(m.group(1)) if m else 60
        result["action"] = f"show_training_below_{thresh}"
        result["data"] = who_needs_training(df, thresh=thresh).to_dict(orient="records")
        result["analysis"] = f"Personnel requiring training below {thresh}% threshold"
        return result
    elif "leaders" in text_low or "leadership" in text_low:
        skill = None
        for s in df["Primary_Skill"].dropna().unique().tolist():
            if s.lower() in text_low:
                skill = s
                break
        tab = leadership_list(df)
        if skill:
            tab = tab[tab["Primary_Skill"].str.lower() == skill.lower()]
        result["action"] = "show_leadership"
        result["data"] = tab.head(50).to_dict(orient="records")
        result["analysis"] = f"Leadership candidates{' for ' + skill if skill else ''}"
        return result
    elif "team" in text_low or "readiness" in text_low:
        m = re.search(r"(\d{1,3})", text_low)
        n = int(m.group(1)) if m else 10
        roles = []
        for s in df["Primary_Skill"].dropna().unique():
            if s.lower() in text_low:
                roles.append(s)
        team = select_best_team(df, headcount=n, required_roles=roles or None)
        result["action"] = "select_team"
        result["data"] = team.to_dict(orient="records")
        result["analysis"] = f"Optimal team of {n} personnel{' with ' + ', '.join(roles) if roles else ''}"
        return result
    else:
        # Default to attrition analysis
        result["action"] = "show_attrition"
        result["data"] = who_is_going_to_leave(df).to_dict(orient="records")
        result["analysis"] = "Personnel at risk of leaving the organization"
    
    return result


def _analyze_retirement_scenario(df: pd.DataFrame, text_low: str, client) -> dict:
    """Analyze impact of retiring officers/personnel"""
    d = add_derived_columns(df)
    
    # Extract retirement criteria
    criteria = []
    if "senior" in text_low or "high" in text_low:
        criteria.append("senior personnel")
    if "officer" in text_low:
        criteria.append("officers")
    if "pilot" in text_low:
        criteria.append("pilots")
    if "engineer" in text_low:
        criteria.append("engineers")
    
    # Find personnel matching criteria
    retirement_candidates = d.copy()
    if "senior" in text_low:
        retirement_candidates = retirement_candidates[retirement_candidates["Years_of_Service"] >= 15]
    if "officer" in text_low:
        retirement_candidates = retirement_candidates[retirement_candidates["Rank"].str.contains("Officer|Captain|Major|Colonel", case=False, na=False)]
    if "pilot" in text_low:
        retirement_candidates = retirement_candidates[retirement_candidates["Primary_Skill"].str.contains("Pilot", case=False, na=False)]
    if "engineer" in text_low:
        retirement_candidates = retirement_candidates[retirement_candidates["Primary_Skill"].str.contains("Engineer", case=False, na=False)]
    
    # Calculate impact metrics
    total_affected = len(retirement_candidates)
    avg_experience = retirement_candidates["Years_of_Service"].mean() if total_affected > 0 else 0
    
    # Handle performance rating as text
    performance_dist = retirement_candidates["Performance_Rating"].value_counts().to_dict() if total_affected > 0 else {}
    leadership_loss = len(retirement_candidates[retirement_candidates["Leadership_Potential"].isin(["High", "Yes"])])
    
    # Generate analysis
    analysis = f"Retirement Impact Analysis:\n"
    analysis += f"• {total_affected} personnel would be affected\n"
    analysis += f"• Average experience loss: {avg_experience:.1f} years\n"
    analysis += f"• Performance distribution: {performance_dist}\n"
    analysis += f"• Leadership potential loss: {leadership_loss} high-potential individuals\n"
    
    recommendations = [
        "Develop succession planning for critical roles",
        "Accelerate leadership development programs",
        "Consider phased retirement to retain knowledge",
        "Implement knowledge transfer protocols"
    ]
    
    return {
        "action": "retirement_impact",
        "analysis": analysis,
        "recommendations": recommendations,
        "data": retirement_candidates[["Personnel_ID", "Name", "Rank", "Primary_Skill", "Years_of_Service", "Performance_Rating", "Leadership_Potential"]].to_dict(orient="records")
    }


def _analyze_redeployment_scenario(df: pd.DataFrame, text_low: str, client) -> dict:
    """Analyze impact of redeploying/transferring personnel"""
    d = add_derived_columns(df)
    
    # Extract redeployment criteria
    from_skill = None
    to_skill = None
    
    skills = df["Primary_Skill"].dropna().unique()
    for skill in skills:
        if skill.lower() in text_low:
            if "from" in text_low and text_low.find(skill.lower()) < text_low.find("from"):
                from_skill = skill
            elif "to" in text_low and text_low.find(skill.lower()) > text_low.find("to"):
                to_skill = skill
            elif not from_skill:
                from_skill = skill
            else:
                to_skill = skill
    
    # Find personnel for redeployment
    if from_skill:
        redeploy_candidates = d[d["Primary_Skill"].str.contains(from_skill, case=False, na=False)]
    else:
        # Handle text-based performance ratings
        redeploy_candidates = d[d["Performance_Rating"].isin(["Below Average", "Average"])]
    
    # Calculate impact
    total_affected = len(redeploy_candidates)
    skill_gaps = {}
    if from_skill:
        remaining = d[~d["Primary_Skill"].str.contains(from_skill, case=False, na=False)]
        skill_gaps[from_skill] = len(remaining[remaining["Primary_Skill"].str.contains(from_skill, case=False, na=False)])
    
    analysis = f"Redeployment Impact Analysis:\n"
    analysis += f"• {total_affected} personnel available for redeployment\n"
    if from_skill and to_skill:
        analysis += f"• Moving from {from_skill} to {to_skill}\n"
    analysis += f"• Skill gap analysis: {skill_gaps}\n"
    
    recommendations = [
        "Assess skill transferability and training needs",
        "Plan for knowledge retention in source roles",
        "Develop cross-training programs",
        "Monitor performance during transition period"
    ]
    
    return {
        "action": "redeployment_impact",
        "analysis": analysis,
        "recommendations": recommendations,
        "data": redeploy_candidates[["Personnel_ID", "Name", "Rank", "Primary_Skill", "Performance_Rating", "Training_Score"]].to_dict(orient="records")
    }


def _analyze_grounding_scenario(df: pd.DataFrame, text_low: str, client) -> dict:
    """Analyze impact of grounding pilots due to medical reasons"""
    d = add_derived_columns(df)
    
    # Find pilots with medical issues
    pilots = d[d["Primary_Skill"].str.contains("Pilot", case=False, na=False)]
    medical_issues = pilots[
        (pilots["Medical_Category"].isin(["C1", "C2"])) |
        (pilots["Medical_Score"] < 70) |
        (pilots["BMI"] > 30) |
        (pilots["BMI"] < 18.5)
    ]
    
    # Calculate impact
    total_pilots = len(pilots)
    grounded_pilots = len(medical_issues)
    operational_impact = (grounded_pilots / total_pilots * 100) if total_pilots > 0 else 0
    
    # Find replacement candidates - handle text-based performance ratings
    replacement_candidates = pilots[
        (pilots["Medical_Category"].isin(["A1", "A2", "B1"])) &
        (pilots["Performance_Rating"].isin(["Excellent", "Good"])) &
        (pilots["Training_Score"] >= 80)
    ]
    
    analysis = f"Pilot Grounding Impact Analysis:\n"
    analysis += f"• {grounded_pilots} pilots would be grounded ({operational_impact:.1f}% of pilot force)\n"
    analysis += f"• {len(replacement_candidates)} pilots available as replacements\n"
    analysis += f"• Operational readiness impact: {'High' if operational_impact > 20 else 'Medium' if operational_impact > 10 else 'Low'}\n"
    
    recommendations = [
        "Implement medical monitoring programs",
        "Develop pilot fitness maintenance protocols",
        "Create backup pilot rotation system",
        "Consider accelerated pilot training programs"
    ]
    
    return {
        "action": "grounding_impact",
        "analysis": analysis,
        "recommendations": recommendations,
        "data": medical_issues[["Personnel_ID", "Name", "Rank", "Medical_Category", "Medical_Score", "BMI", "Performance_Rating"]].to_dict(orient="records")
    }


def _analyze_promotion_scenario(df: pd.DataFrame, text_low: str, client) -> dict:
    """Analyze impact of promoting personnel"""
    d = add_derived_columns(df)
    
    # Find promotion candidates - handle text-based performance ratings
    promotion_candidates = d[
        (d["Leadership_Potential"].isin(["High", "Yes"])) &
        (d["Performance_Rating"].isin(["Excellent", "Good"])) &
        (d["Years_of_Service"] >= 5)
    ].sort_values(["Leadership_Score", "Performance_Rating"], ascending=[False, False])
    
    # Calculate impact
    total_candidates = len(promotion_candidates)
    skill_distribution = promotion_candidates["Primary_Skill"].value_counts().to_dict()
    
    analysis = f"Promotion Impact Analysis:\n"
    analysis += f"• {total_candidates} personnel eligible for promotion\n"
    analysis += f"• Skill distribution: {skill_distribution}\n"
    analysis += f"• Leadership pipeline strength: {'Strong' if total_candidates > 20 else 'Moderate' if total_candidates > 10 else 'Weak'}\n"
    
    recommendations = [
        "Implement structured promotion criteria",
        "Develop leadership development programs",
        "Create mentorship opportunities",
        "Plan for role transitions and knowledge transfer"
    ]
    
    return {
        "action": "promotion_impact",
        "analysis": analysis,
        "recommendations": recommendations,
        "data": promotion_candidates[["Personnel_ID", "Name", "Rank", "Primary_Skill", "Leadership_Potential", "Performance_Rating", "Years_of_Service"]].to_dict(orient="records")
    }


def _analyze_budget_scenario(df: pd.DataFrame, text_low: str, client) -> dict:
    """Analyze budget/financial impact scenarios"""
    d = add_derived_columns(df)
    
    # Calculate cost metrics
    total_personnel = len(d)
    avg_training_cost = d["Training_Score"].mean() * 100  # Estimated cost per person
    avg_medical_cost = d["Medical_Score"].mean() * 50     # Estimated medical cost
    
    # Find high-cost personnel - handle text-based performance ratings
    high_cost_personnel = d[
        (d["Training_Score"] > 80) |
        (d["Medical_Score"] < 70) |
        (d["Performance_Rating"].isin(["Below Average", "Average"]))
    ]
    
    analysis = f"Budget Impact Analysis:\n"
    analysis += f"• Total personnel: {total_personnel}\n"
    analysis += f"• Estimated training costs: ${avg_training_cost * total_personnel:,.0f}\n"
    analysis += f"• Estimated medical costs: ${avg_medical_cost * total_personnel:,.0f}\n"
    analysis += f"• High-cost personnel: {len(high_cost_personnel)}\n"
    
    recommendations = [
        "Implement cost optimization strategies",
        "Focus training investments on high-potential personnel",
        "Develop preventive medical programs",
        "Consider performance-based resource allocation"
    ]
    
    return {
        "action": "budget_impact",
        "analysis": analysis,
        "recommendations": recommendations,
        "data": high_cost_personnel[["Personnel_ID", "Name", "Rank", "Primary_Skill", "Training_Score", "Medical_Score", "Performance_Rating"]].to_dict(orient="records")
    }



def get_readiness_data():
    # Placeholder logic — safe to expand later
    return {
        "status": "System operational",
        "last_updated": "N/A",
        "metrics": {}
    }

