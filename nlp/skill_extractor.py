import re
from typing import List, Dict, Set, Tuple

# Comprehensive taxonomy of in-demand technology skills with category mapping
SKILL_TAXONOMY = {
    # 1. Programming Languages
    "Python": {"category": "Languages", "aliases": ["python", "python3", "py"]},
    "JavaScript": {"category": "Languages", "aliases": ["javascript", "js", "ecmascript"]},
    "TypeScript": {"category": "Languages", "aliases": ["typescript", "ts"]},
    "Java": {"category": "Languages", "aliases": ["java", "core java", "j2ee"]},
    "C++": {"category": "Languages", "aliases": ["c++", "cpp"]},
    "C#": {"category": "Languages", "aliases": ["c#", "csharp", "c sharp", ".net c#"]},
    "Go": {"category": "Languages", "aliases": ["golang", "go language", "go lang"]},
    "Rust": {"category": "Languages", "aliases": ["rust", "rustlang"]},
    "Ruby": {"category": "Languages", "aliases": ["ruby"]},
    "PHP": {"category": "Languages", "aliases": ["php", "php8"]},
    "Swift": {"category": "Languages", "aliases": ["swift", "swiftui"]},
    "Kotlin": {"category": "Languages", "aliases": ["kotlin"]},
    "R": {"category": "Languages", "aliases": ["r programming", "r-lang", "r language"]},
    "Scala": {"category": "Languages", "aliases": ["scala"]},

    # 2. Frameworks & Web Backend/Frontend
    "Django": {"category": "Frameworks", "aliases": ["django", "django rest framework", "drf"]},
    "Flask": {"category": "Frameworks", "aliases": ["flask"]},
    "FastAPI": {"category": "Frameworks", "aliases": ["fastapi", "fast-api"]},
    "React": {"category": "Frameworks", "aliases": ["react", "react.js", "reactjs", "react native"]},
    "Node.js": {"category": "Frameworks", "aliases": ["node.js", "nodejs", "node js", "node"]},
    "Express": {"category": "Frameworks", "aliases": ["express.js", "expressjs", "express"]},
    "Vue.js": {"category": "Frameworks", "aliases": ["vue", "vue.js", "vuejs"]},
    "Angular": {"category": "Frameworks", "aliases": ["angular", "angularjs", "angular 2+"]},
    "Next.js": {"category": "Frameworks", "aliases": ["next.js", "nextjs", "next js"]},
    "Spring Boot": {"category": "Frameworks", "aliases": ["spring boot", "springboot", "spring framework", "spring"]},
    "ASP.NET": {"category": "Frameworks", "aliases": ["asp.net", "asp net", ".net core", "dotnet"]},
    "Ruby on Rails": {"category": "Frameworks", "aliases": ["rails", "ruby on rails", "ror"]},
    "GraphQL": {"category": "Frameworks", "aliases": ["graphql", "graph ql"]},
    "REST APIs": {"category": "Frameworks", "aliases": ["rest api", "rest apis", "restful", "restful api"]},

    # 3. Databases & Caching
    "SQL": {"category": "Databases", "aliases": ["sql", "structured query language", "relational database"]},
    "PostgreSQL": {"category": "Databases", "aliases": ["postgresql", "postgres", "psql"]},
    "MySQL": {"category": "Databases", "aliases": ["mysql", "mariadb"]},
    "MongoDB": {"category": "Databases", "aliases": ["mongodb", "mongo", "nosql"]},
    "Redis": {"category": "Databases", "aliases": ["redis"]},
    "SQLite": {"category": "Databases", "aliases": ["sqlite", "sqlite3"]},
    "DynamoDB": {"category": "Databases", "aliases": ["dynamodb", "aws dynamodb"]},
    "Elasticsearch": {"category": "Databases", "aliases": ["elasticsearch", "elastic search", "opensearch"]},
    "Cassandra": {"category": "Databases", "aliases": ["cassandra", "apache cassandra"]},
    "Oracle": {"category": "Databases", "aliases": ["oracle db", "oracle database", "pl/sql", "plsql"]},

    # 4. AI / Machine Learning & Data Science
    "Machine Learning": {"category": "AI & ML", "aliases": ["machine learning", "ml", "statistical learning"]},
    "Deep Learning": {"category": "AI & ML", "aliases": ["deep learning", "dl", "neural networks", "deep neural networks"]},
    "LLMs": {"category": "AI & ML", "aliases": ["llm", "llms", "large language model", "large language models", "rag", "retrieval augmented generation"]},
    "Generative AI": {"category": "AI & ML", "aliases": ["generative ai", "genai", "gen ai", "gpt", "openai", "claude"]},
    "LangChain": {"category": "AI & ML", "aliases": ["langchain", "llamaindex", "llama-index"]},
    "PyTorch": {"category": "AI & ML", "aliases": ["pytorch", "torch"]},
    "TensorFlow": {"category": "AI & ML", "aliases": ["tensorflow", "tf", "keras"]},
    "Scikit-learn": {"category": "AI & ML", "aliases": ["scikit-learn", "sklearn", "scikit learn"]},
    "NLP": {"category": "AI & ML", "aliases": ["nlp", "natural language processing", "text mining", "spacy", "nltk", "transformers"]},
    "Computer Vision": {"category": "AI & ML", "aliases": ["computer vision", "cv", "opencv", "yolo"]},
    "Pandas": {"category": "AI & ML", "aliases": ["pandas"]},
    "NumPy": {"category": "AI & ML", "aliases": ["numpy"]},
    "Hugging Face": {"category": "AI & ML", "aliases": ["hugging face", "huggingface", "transformers library"]},

    # 5. Cloud & DevOps
    "AWS": {"category": "Cloud & DevOps", "aliases": ["aws", "amazon web services", "ec2", "s3", "lambda"]},
    "Azure": {"category": "Cloud & DevOps", "aliases": ["azure", "microsoft azure"]},
    "Google Cloud": {"category": "Cloud & DevOps", "aliases": ["gcp", "google cloud", "google cloud platform"]},
    "Docker": {"category": "Cloud & DevOps", "aliases": ["docker", "containerization", "containers"]},
    "Kubernetes": {"category": "Cloud & DevOps", "aliases": ["kubernetes", "k8s"]},
    "CI/CD": {"category": "Cloud & DevOps", "aliases": ["ci/cd", "ci cd", "continuous integration", "github actions", "gitlab ci"]},
    "Terraform": {"category": "Cloud & DevOps", "aliases": ["terraform", "iac", "infrastructure as code"]},
    "Linux": {"category": "Cloud & DevOps", "aliases": ["linux", "unix", "ubuntu", "bash", "shell scripting"]},
    "Git": {"category": "Cloud & DevOps", "aliases": ["git", "github", "gitlab", "version control"]},
    "Jenkins": {"category": "Cloud & DevOps", "aliases": ["jenkins"]},
    "Ansible": {"category": "Cloud & DevOps", "aliases": ["ansible"]},

    # 6. Big Data & Analytics
    "Apache Spark": {"category": "Big Data", "aliases": ["spark", "apache spark", "pyspark"]},
    "Kafka": {"category": "Big Data", "aliases": ["kafka", "apache kafka"]},
    "Snowflake": {"category": "Big Data", "aliases": ["snowflake"]},
    "Databricks": {"category": "Big Data", "aliases": ["databricks"]},
    "Airflow": {"category": "Big Data", "aliases": ["airflow", "apache airflow"]},
    "Tableau": {"category": "Big Data", "aliases": ["tableau"]},
    "Power BI": {"category": "Big Data", "aliases": ["power bi", "powerbi"]}
}

class SkillExtractor:
    """
    Intelligent skill extraction engine that scans job titles and descriptions
    for technical skills with word-boundary and alias normalization.
    """

    def __init__(self):
        # Precompile regex patterns for efficiency
        self.compiled_patterns = {}
        for skill, data in SKILL_TAXONOMY.items():
            patterns = []
            for alias in data["aliases"]:
                # Escape special regex characters like +, #, .
                escaped = re.escape(alias)
                # Word boundary check, allowing for punctuation like C++, C#, .NET
                if alias in ["c", "r", "go"]:
                    # Strict pattern for very short words to prevent false positives
                    pat = rf"(?:^|[\s,;./(]){escaped}(?:[\s,;./)]|$)"
                else:
                    pat = rf"\b{escaped}\b"
                patterns.append(pat)
            combined = re.compile("|".join(patterns), re.IGNORECASE)
            self.compiled_patterns[skill] = combined

    def extract_skills(self, text: str) -> List[Dict[str, str]]:
        """
        Extract unique matching skills from arbitrary text (job description or resume).
        Returns list of dicts with skill name and category.
        """
        if not text:
            return []

        matched_skills = []
        for skill_name, pattern in self.compiled_patterns.items():
            if pattern.search(text):
                matched_skills.append({
                    "name": skill_name,
                    "category": SKILL_TAXONOMY[skill_name]["category"]
                })

        return matched_skills

    def extract_skill_names(self, text: str) -> List[str]:
        """Returns just a list of skill name strings."""
        return [s["name"] for s in self.extract_skills(text)]

    def get_category_counts(self, skill_list: List[str]) -> Dict[str, int]:
        """Aggregates skills into their respective domains."""
        counts = {}
        for skill in skill_list:
            if skill in SKILL_TAXONOMY:
                cat = SKILL_TAXONOMY[skill]["category"]
                counts[cat] = counts.get(cat, 0) + 1
        return counts

    @staticmethod
    def get_all_skills() -> List[Dict[str, str]]:
        """Returns the full master catalog of tracked skills."""
        return [
            {"name": k, "category": v["category"], "aliases": v["aliases"]}
            for k, v in SKILL_TAXONOMY.items()
        ]

# Global instance for app-wide use
skill_extractor = SkillExtractor()
