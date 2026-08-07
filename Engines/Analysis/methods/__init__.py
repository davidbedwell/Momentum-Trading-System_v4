from .base import AnalysisMethod, AnalysisServices, MethodResult, MethodValidationResult
from .comparison import CohortOutcomeComparisonMethod
from .descriptive import DescriptiveStatisticsMethod
from .foundation import FoundationDatasetIntrospectionMethod
from .relationship import RelationshipRedundancyMethod
from .reliability import BasicStatisticalReliabilityMethod

INITIAL_METHODS = (
    FoundationDatasetIntrospectionMethod(),
    DescriptiveStatisticsMethod(),
    CohortOutcomeComparisonMethod(),
    RelationshipRedundancyMethod(),
    BasicStatisticalReliabilityMethod(),
)

__all__ = [
    "AnalysisMethod",
    "AnalysisServices",
    "MethodResult",
    "MethodValidationResult",
    "FoundationDatasetIntrospectionMethod",
    "DescriptiveStatisticsMethod",
    "CohortOutcomeComparisonMethod",
    "RelationshipRedundancyMethod",
    "BasicStatisticalReliabilityMethod",
    "INITIAL_METHODS",
]
