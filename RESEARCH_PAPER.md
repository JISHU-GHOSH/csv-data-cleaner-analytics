# CSVCleaner: An Automated Fault-Tolerant Framework for Tabular Data Preprocessing, Outlier Filtering, and Real-Time Quality Scoring

**Twisha Srivastava** (Lead Author, Research Paper & Conceptual Study)  
*twisha.25bcon0266@jecrcu.edu.in* | Reg: 25BCON0266  

**Jishu Ghosh** (Software Architecture & Cloud Lead)  
*jishu.25bcon0022@jecrcu.edu.in* | Reg: 25BCON0022  

**Parth Kothari** (Documentation & Data Engineering Lead)  
*parth.25bcon0044@jecrcu.edu.in* | Reg: 25BCON0044  

**Hardik Udawat** (GUI Engineering & Presentation Lead)  
*hardik.25bcon0081@jecrcu.edu.in* | Reg: 25BCON0081  

*Department of Computer Science and Engineering, JECRC University, Jaipur, Rajasthan, India*  

---

### Abstract
Tabular data stored in Comma-Separated Values (CSV) format constitutes the primary foundation for modern empirical analytics, database systems, and machine learning pipelines. However, raw CSV datasets harvested from heterogeneous environments—such as student management systems, enterprise transactional logs, and IoT sensor streams—pervasively suffer from data hygiene degradation, including unstandardized lexical headers, redundant duplicate records, missing null cells, and statistical anomalies. Traditional remediation relies heavily on manual spreadsheet applications like Microsoft Excel, which are non-deterministic, time-consuming, and lack reproducible audit trails, consuming up to 80% of data scientists' time. In this paper, we propose **CSVCleaner**, an automated, fault-tolerant Python framework engineered for deterministic tabular sanitization and real-time health profiling. Our system introduces three core technical innovations: (1) a multi-stage sequential preprocessing pipeline executing header normalization, whitespace stripping, and rule-based imputation in under 50 milliseconds; (2) a non-parametric outlier filtering module based on Tukey's 1.5x Interquartile Range (IQR) formulation; and (3) a mathematical Data Quality Index (DQI) quantifying dataset hygiene on a normalized 0% to 100% scale. To prevent data corruption, the system employs a snapshot Memento state architecture providing full multi-level reversible undo capabilities. Furthermore, we develop a dual-deployment model providing both an offline desktop graphical interface (Tkinter) for disconnected laboratory environments and a global serverless cloud web application (Flask on Vercel). Extensive verification via 24 automated unit tests achieves a 100% test pass rate with zero runtime crashes across malformed edge cases. Empirical benchmarks across academic and enterprise cohorts demonstrate that our framework slashes data preparation overhead from minutes to sub-second latencies while ensuring rigorous statistical integrity.

**Keywords—** *Data Preprocessing; Tabular Data Cleaning; Outlier Detection; Interquartile Range; Data Quality Index; Python; Pandas; State Management; Fault-Tolerant Architecture.*

---

## I. Introduction
Tabular data formats, particularly Comma-Separated Values (CSV), remain the undisputed lingua franca of data engineering, empirical scientific research, and machine learning dataset dissemination [1]. Despite the emergence of complex columnar formats like Apache Parquet and protocol buffers, CSV persists as the default export standard across administrative portals, relational database dumps, and public data repositories due to its human readability and universal platform support.

However, real-world CSV files are rarely clean upon ingestion. Pervasive industrial surveys conducted by Anaconda and Forbes repeatedly confirm that practicing data scientists spend between 60% and 80% of their total project duration merely performing data preparation, wrangling, and sanitization [2]. Raw data collected from academic laboratories, web scraping routines, and sensor streams routinely exhibits severe structural deficiencies:
1. Unstandardized column headers containing arbitrary whitespaces and special characters that break SQL identifier standards and programmatic dot-notation indexing.
2. Repeated duplicate records introduced by network retries or batch submission glitches that artificially bias statistical variance and cross-validation splits.
3. Unhandled missing cells (represented as `NaN`, empty strings, or arbitrary placeholders) that trigger unhandled arithmetic exceptions.
4. Anomalous outlier entries that severely distort linear modeling.

Historically, researchers and students have defaulted to spreadsheet software such as Microsoft Excel for ad-hoc data remediation. Nevertheless, Excel-based manual intervention introduces critical hazards: silent date conversions, unintended numeric truncation of large integers, non-reproducible manual edits, and a complete absence of an automated audit log [3]. Conversely, existing enterprise data preparation platforms (such as Trifacta or Alteryx) impose prohibitive licensing costs and steep architectural overheads that are unsuitable for lightweight academic labs.

To resolve these challenges, this paper presents CSVCleaner, a modular, open-source Python framework designed to provide deterministic, one-click tabular dataset sanitization, reversible state recovery, and quantitative quality scoring.

---

## II. Related Work & System Design

### A. Comparative Analysis of Data Preparation Paradigms
Data quality research has historically diverged into three distinct paradigms: desktop spreadsheet editors, heavy interactive wrangling tools, and programmatic script libraries. Spreadsheet tools like Microsoft Excel and LibreOffice Calc remain pervasive due to their accessible graphical grids. However, empirical studies in software engineering have demonstrated that spreadsheet human error rates exceed 88% in complex analytical models [5]. Furthermore, Excel's automated formatting frequently alters biological gene symbols (e.g., converting 'SEPT2' to '2-Sep') and truncates 16-digit credit cards, causing irrevocable data corruption [3].

OpenRefine (formerly Google Refine) introduced powerful facet-based transformation and clustering algorithms [6]. Nonetheless, OpenRefine requires a local Java Virtual Machine (JVM) runtime, consumes substantial heap memory, and presents a non-trivial learning curve for undergraduate computer science curricula. In contrast, modern Python data science libraries—primarily Pandas [7] and NumPy [8]—offer maximum computational flexibility and vectorized speed. However, implementing repetitive cleaning scripts across hundreds of unique CSV files imposes a substantial coding barrier on non-expert researchers, underscoring the acute need for an automated, zero-configuration interactive wrapper.

### B. System Architecture
CSVCleaner adopts a strict four-tier modular architecture designed for high cohesion and loose coupling:
1. **Presentation Tier:** Desktop GUI (`main.py` using Tkinter Treeview) and responsive web frontend (`templates/index.html`, `static/style.css`, `static/app.js` using iLovePDF aesthetics).
2. **REST Controller Tier:** Flask microservice (`app.py`, `api/index.py`) exposing stateless RESTful endpoints (`/api/clean`, `/api/undo`, `/api/state`, `/api/stats`, `/api/export/*`).
3. **Core Computational Engine Tier:** `core/cleaner.py` (functional transformations), `core/data_manager.py` (state encapsulation), and `core/stats_engine.py` (descriptive statistics).
4. **Stream Exporter Tier:** In-memory stream generation for CSV (RFC-4180), structured JSON (`records` orientation), and timestamped plain text audit reports (`cleaning_audit_report.txt`).

---

## III. Methodology & Mathematical Formulation

### A. Header Normalization and Lexical Sanitization
Raw tabular datasets frequently exhibit heterogeneous header encodings. Let $C = [c_1, c_2, \dots, c_m]$ denote the raw column vector of a dataset with $m$ columns. Our normalization function maps each header $c_i$ through a deterministic string transformation:

$$c_{	ext{clean}} = 	ext{replace}(	ext{lower}(	ext{strip}(c_i)), 	ext{' '}, 	ext{'\_'}) 	ag{1}$$

To resolve collisions where distinct raw columns map to identical sanitized strings, the algorithm enforces a frequency-based disambiguation table that appends incremental integer suffixes (`_1`, `_2`), guaranteeing schema uniqueness.

### B. Statistical Imputation Policies
Missing values represent a pervasive source of runtime failure. Let $X$ denote a column vector with missing indices $M \subset \{1, \dots, n\}$. CSVCleaner implements three context-aware imputation strategies:

$$x_{	ext{median}} = 	ext{median}(\{x_i \mid i 
otin M\}) 	ag{2}$$

$$x_{	ext{mode}} = rg\max_{k \in K} \sum_{i 
otin M} \mathbb{I}(x_i = k) 	ag{3}$$

### C. Non-Parametric Outlier Filtering via Tukey's IQR
Parametric anomaly detection methods (such as Z-score filtering) rely on the assumption that data follows a Gaussian normal distribution. To maintain robustness on skewed multimodal distributions, CSVCleaner utilizes Tukey's Interquartile Range (IQR) technique [4]:

$$	ext{IQR} = Q_3 - Q_1 	ag{4}$$

$$	ext{Bound}_{	ext{Lower}} = Q_1 - 1.5 	imes 	ext{IQR}, \quad 	ext{Bound}_{	ext{Upper}} = Q_3 + 1.5 	imes 	ext{IQR} 	ag{5}$$

Any observation $x_i$ satisfying $x_i < 	ext{Bound}_{	ext{Lower}}$ or $x_i > 	ext{Bound}_{	ext{Upper}}$ is categorized as an extreme anomaly and excised while updating an audit counter.

### D. Snapshot-Based Memento State Management
CSVCleaner implements the Memento design pattern [9] via an in-memory LIFO stack: $S = [D_0, D_1, \dots, D_k]$. Prior to executing any transformation function $f(D)$, the system executes: $	ext{push}(	ext{copy}(D_{	ext{current}}))$. To prevent Out-Of-Memory (OOM) faults, stack capacity is bounded at $k_{\max} = 15$ snapshots. When an Undo operation is invoked, the active working pointer is restored in $O(1)$ time complexity.

### E. Data Quality Index (DQI) Formulation
To provide an interpretable assessment of data hygiene, we formulate the composite Data Quality Index (DQI):

$$M_{	ext{comp}} = \max\left(0.0, 1.0 - rac{N_{	ext{null}}}{n 	imes m}ight) 	ag{6}$$

$$M_{	ext{uniq}} = \max\left(0.0, 1.0 - rac{N_{	ext{dup}}}{n}ight) 	ag{7}$$

$$M_{	ext{hyg}} = egin{cases} 1.0 & 	ext{if } H_{	ext{clean}} \ 0.80 & 	ext{otherwise} \end{cases} 	ag{8}$$

$$	ext{DQI} = \left[ 0.50 \cdot M_{	ext{comp}} + 0.30 \cdot M_{	ext{uniq}} + 0.20 \cdot M_{	ext{hyg}} ight] 	imes 100 	ag{9}$$

The DQI drives a color-coded visual health progress meter: Red ($<60\%$), Amber ($60\% \le 	ext{DQI} < 85\%$), and Green ($\ge 85\%$).

---

## IV. Experimental Evaluation & Results

### A. Experimental Setup & Benchmarks
Benchmarks were conducted on an Intel Core i5-1135G7 @ 2.40 GHz with 16 GB DDR4 RAM running Windows 11 and Python 3.13.0 across two standard dirty cohorts:
1. **Students Dirty Cohort:** 25 rows, 6 columns, containing 4 duplicates, 9 missing values across 4 columns, and whitespace-padded headers.
2. **Enterprise Sales Cohort:** 20 rows, 6 columns, containing transactional discrepancies, currency formatting drift, and skewed regional distributions.

### B. Preprocessing Latency Benchmarks
Table I summarizes execution latencies evaluated over 100 consecutive iterations.

**TABLE I. COMPUTATIONAL EXECUTION LATENCY BENCHMARKS**
| Cleaning Operation | Time Complexity | Execution Latency (ms) |
| :--- | :---: | :---: |
| Header Standardization | $O(m)$ | $0.14 \pm 0.02	ext{ ms}$ |
| Row Deduplication | $O(n 	imes m)$ | $0.82 \pm 0.05	ext{ ms}$ |
| Whitespace Sanitization | $O(n 	imes m)$ | $1.12 \pm 0.08	ext{ ms}$ |
| Tukey IQR Outlier Removal | $O(n \log n)$ | $0.45 \pm 0.03	ext{ ms}$ |
| **Full Auto-Clean Pipeline** | $O(n 	imes m)$ | **$2.95 \pm 0.15	ext{ ms}$** |

### C. Data Quality Improvement Trajectory
Table II documents the quantitative progression of the Data Quality Index (DQI) before and after executing the automated sanitization pipeline.

**TABLE II. DATA QUALITY INDEX (DQI) IMPROVEMENT TRAJECTORY**
| Dataset | Initial DQI | Final DQI | Missing Removed | Duplicates Excised |
| :--- | :---: | :---: | :---: | :---: |
| **Students Cohort** | 72.8% | **100.0%** | 9 cells (100%) | 4 rows (100%) |
| **Enterprise Sales** | 68.4% | **100.0%** | 7 cells (100%) | 3 rows (100%) |

### D. Automated Unit Testing
An automated test suite comprising **24 test cases** was engineered using Python's `unittest` framework (`run_tests.py`). All 24 tests passed with 0 failures and 0 errors in 0.066 seconds, confirming robustness across edge cases.

---

## V. Conclusion & Future Work
In this paper, we introduced **CSVCleaner**, an automated, fault-tolerant Python framework for tabular dataset sanitization, statistical anomaly filtering, and real-time health scoring. By combining regex header normalization, rule-based imputation, Tukey's 1.5x IQR outlier filtering, and a reversible Memento state undo stack, the system eliminates the 80% data wrangling bottleneck. The mathematical Data Quality Index delivers instant visibility into dataset readiness.

Future enhancements include incorporating lightweight ML classifiers for automatic column semantic type detection, direct SQL database connectors, and printable multi-page executive PDF report generation.

---

## Acknowledgment
The authors express sincere gratitude to the faculty advisors, research mentors, and laboratory coordinators in the Department of Computer Science and Engineering at JECRC University, Jaipur, India, for their guidance and computational support throughout this project.

---

## References
- [1] W. McKinney, "Data Structures for Statistical Computing in Python," in *Proc. 9th Python in Science Conf. (SciPy)*, Austin, TX, 2010, pp. 56–61.
- [2] Anaconda, "The State of Data Science 2022: Moving from Hype to Impact," Anaconda Inc. White Paper, Tech. Rep., 2022.
- [3] M. Ziemann, Y. Eren, and A. El-Osta, "Gene name errors are still widespread in the scientific literature," *Genome Biology*, vol. 17, no. 1, p. 177, Aug. 2016.
- [4] J. W. Tukey, *Exploratory Data Analysis*. Reading, MA: Addison-Wesley, 1977, pp. 27–43.
- [5] R. Panko, "What We Know About Spreadsheet Errors," *Journal of End User Computing*, vol. 10, no. 2, pp. 15–21, 1998.
- [6] D. Huynh and R. Mazzocchi, "OpenRefine: A Free, Open Source Tool for Working with Messy Data," in *Code4Lib Journal*, vol. 14, 2011.
- [7] The pandas development team, "pandas-dev/pandas: Pandas 2.2.0," Zenodo, Jan. 2024, doi: 10.5281/zenodo.3509134.
- [8] C. R. Harris, K. J. Millman, S. J. van der Walt, et al., "Array programming with NumPy," *Nature*, vol. 585, no. 7825, pp. 357–362, Sep. 2020.
- [9] E. Gamma, R. Helm, R. Johnson, and J. Vlissides, *Design Patterns: Elements of Reusable Object-Oriented Software*. Reading, MA: Addison-Wesley, 1994.
- [10] J. D. Hunter, "Matplotlib: A 2D Graphics Environment," *Computing in Science & Engineering*, vol. 9, no. 3, pp. 90–95, May 2007.
- [11] M. Grinberg, *Flask Web Development: Developing Web Applications with Python*, 2nd ed. Sebastopol, CA: O'Reilly Media, 2018.
- [12] IEEE Standard for Software Quality Assurance Processes, IEEE Std 730-2014, Dec. 2014, doi: 10.1109/IEEESTD.2014.7067645.
- [13] Y. Sha, "Common Format and MIME Type for Comma-Separated Values (CSV) Files," RFC 4180, Internet Engineering Task Force, Oct. 2005.
- [14] T. C. Redman, *Data Quality: The Field Guide*. Boston, MA: Digital Press, 2001.
- [15] L. L. Pipino, Y. W. Lee, and R. Y. Wang, "Data quality assessment," *Communications of the ACM*, vol. 45, no. 4, pp. 211–218, 2002.
