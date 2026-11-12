"""Domain skill taxonomy, alias normalization, and keyword-based skill extraction."""

from __future__ import annotations

import re
from typing import Dict, List, Tuple

# Mapping of Category -> {Canonical Skill Name: [aliases/patterns]}
SKILL_TAXONOMY: Dict[str, Dict[str, List[str]]] = {
    "Programming Languages": {
        "Python": ["python", "python3"],
        "Java": ["java"],
        "JavaScript": ["javascript", "ecmascript", "es6"],
        "TypeScript": ["typescript"],
        "C++": ["c++", "cpp"],
        "C#": ["c#", "csharp"],
        "C": ["c language", "embedded c"],
        "Go": ["golang", "go language"],
        "Rust": ["rust"],
        "R": ["r programming", "r language", "rstudio"],
        "SQL": ["sql", "t-sql", "pl/sql"],
        "Scala": ["scala"],
        "PHP": ["php"],
        "Ruby": ["ruby"],
        "Bash/Shell": ["bash", "shell scripting", "powershell"],
    },
    "AI, ML & Data Science": {
        "Machine Learning": ["machine learning", "ml"],
        "Deep Learning": ["deep learning", "dl", "neural networks", "neural network"],
        "NLP": ["nlp", "natural language processing"],
        "Computer Vision": ["computer vision", "opencv"],
        "Scikit-learn": ["scikit-learn", "scikit learn", "sklearn"],
        "TensorFlow": ["tensorflow", "tf"],
        "PyTorch": ["pytorch"],
        "Keras": ["keras"],
        "HuggingFace": ["huggingface", "hugging face", "transformers"],
        "LangChain": ["langchain"],
        "LLMs": ["llm", "llms", "large language models", "large language model", "gpt", "generative ai", "genai"],
        "RAG": ["rag", "retrieval augmented generation"],
        "Pandas": ["pandas"],
        "NumPy": ["numpy"],
        "SciPy": ["scipy"],
        "NLTK": ["nltk"],
        "spaCy": ["spacy"],
        "XGBoost": ["xgboost"],
        "LightGBM": ["lightgbm"],
        "Feature Engineering": ["feature engineering"],
        "Data Analysis": ["data analysis", "exploratory data analysis", "eda"],
        "Data Visualization": ["data visualization", "matplotlib", "seaborn", "plotly", "tableau", "power bi", "powerbi"],
        "Statistics": ["statistics", "statistical modeling", "hypothesis testing", "a/b testing"],
    },
    "Web & Backend": {
        "Flask": ["flask"],
        "Django": ["django"],
        "FastAPI": ["fastapi"],
        "React": ["react", "reactjs", "react.js"],
        "Next.js": ["next.js", "nextjs"],
        "Angular": ["angular", "angularjs"],
        "Vue.js": ["vue", "vuejs", "vue.js"],
        "Node.js": ["node.js", "nodejs"],
        "Express.js": ["express", "express.js", "expressjs"],
        "Spring Boot": ["spring boot", "springboot"],
        "ASP.NET": ["asp.net", ".net", "dotnet"],
        "HTML5": ["html", "html5"],
        "CSS3": ["css", "css3", "tailwind", "tailwindcss", "bootstrap"],
        "REST API": ["rest", "rest api", "restful", "restful apis"],
        "GraphQL": ["graphql"],
        "Microservices": ["microservices", "microservice architecture"],
    },
    "Databases & Big Data": {
        "PostgreSQL": ["postgresql", "postgres"],
        "MySQL": ["mysql"],
        "MongoDB": ["mongodb", "mongo"],
        "Redis": ["redis"],
        "SQLite": ["sqlite"],
        "Elasticsearch": ["elasticsearch", "elastic search"],
        "Snowflake": ["snowflake"],
        "BigQuery": ["bigquery"],
        "Apache Spark": ["spark", "apache spark", "pyspark"],
        "Kafka": ["kafka", "apache kafka"],
        "Airflow": ["airflow", "apache airflow"],
        "ETL": ["etl", "elt", "data pipeline", "data pipelines"],
    },
    "Cloud & DevOps": {
        "AWS": ["aws", "amazon web services", "ec2", "s3", "lambda", "sagemaker"],
        "Azure": ["azure", "microsoft azure"],
        "GCP": ["gcp", "google cloud", "google cloud platform"],
        "Docker": ["docker", "containerization"],
        "Kubernetes": ["kubernetes", "k8s"],
        "CI/CD": ["ci/cd", "cicd", "github actions", "jenkins", "gitlab ci"],
        "Terraform": ["terraform"],
        "Linux": ["linux", "ubuntu", "unix"],
        "Git": ["git", "github", "gitlab", "bitbucket"],
        "MLOps": ["mlops", "mlflow", "dvc"],
    },
    "Engineering & Soft Skills": {
        "Agile/Scrum": ["agile", "scrum", "kanban", "jira"],
        "Unit Testing": ["unit testing", "pytest", "jest", "junit", "tdd"],
        "System Design": ["system design", "distributed systems", "scalability"],
        "Leadership": ["leadership", "mentoring", "team lead", "cross-functional"],
        "Communication": ["communication", "stakeholder management", "presentation"],
        "Problem Solving": ["problem solving", "problem-solving", "analytical thinking"],
    },
}


def _compile_skill_patterns() -> List[Tuple[str, str, re.Pattern[str]]]:
    compiled: List[Tuple[str, str, re.Pattern[str]]] = []
    for category, skills in SKILL_TAXONOMY.items():
        for canonical, aliases in skills.items():
            # Sort longest first so multi-word phrases match before single tokens
            sorted_aliases = sorted(aliases, key=len, reverse=True)
            escaped = [re.escape(alias) for alias in sorted_aliases]
            # Use lookaround boundaries that work with symbols like c++, c#, .net
            pattern = re.compile(
                r"(?<![A-Za-z0-9_])(?:" + "|".join(escaped) + r")(?![A-Za-z0-9_])",
                re.IGNORECASE,
            )
            compiled.append((category, canonical, pattern))
    return compiled


_COMPILED_PATTERNS = _compile_skill_patterns()


def extract_skills(text: str) -> Dict[str, object]:
    """
    Extract canonical skills and their categories from raw text.

    Returns:
        {
            "skills": ["Python", "Flask", ...],          # sorted flat list
            "by_category": {"Programming Languages": [...], ...}
        }
    """
    if not text:
        return {"skills": [], "by_category": {}}

    found_skills: List[str] = []
    by_category: Dict[str, List[str]] = {}

    for category, canonical, pattern in _COMPILED_PATTERNS:
        if pattern.search(text):
            found_skills.append(canonical)
            by_category.setdefault(category, []).append(canonical)

    # Sort deterministically
    found_skills = sorted(set(found_skills))
    for cat in by_category:
        by_category[cat] = sorted(set(by_category[cat]))

    return {
        "skills": found_skills,
        "by_category": by_category,
    }

