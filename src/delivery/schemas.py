from typing import TypedDict
from enum import Enum

class Severity(str, Enum):
  Ok = 'ok' # no concern
  Info = 'info' # minor note
  Warning = 'warning' # should fix, not blocking
  Critical = 'critical' # blocks delivery

# syntax validation, security risks, maintainability, coding standards, potential bugs
class Category(str, Enum):
  SYNTAX = "syntax"
  SECURITY = "security"
  MAINTAINABILITY = "maintainability"
  STANDARDS = "coding_standards"
  BUGS = "potential_bugs"

class Finding(TypedDict):
  category: str # category value above
  severity: str # severity value above
  comment: str 

class ReviewReport(TypedDict):
  findings: list[Finding] # one per cate
  passed: bool # false if any finding is critical
  summary: str 