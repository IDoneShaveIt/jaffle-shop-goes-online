from datetime import datetime
from typing import Optional

from elementary.clients.dbt.dbt_runner import DbtRunner
from pydantic import BaseModel

from data_creation.data_injection.injectors.tests.tests_injector import (
    TestSchema,
    TestSubTypes,
    TestTypes,
    TestsInjector,
)


class TestResult(BaseModel):
    test_timestamp: datetime
    test_status: str
    result_description: str


class DbtTestResult(TestResult):
    test_result_rows: list[dict]


class AnomalyTestMetric(BaseModel):
    value: float
    min_value: float
    max_value: float
    start_time: Optional[str]
    end_time: str

    @property
    def is_anomalous(self):
        return (self.value < self.min_value) or (self.value > self.max_value)


class AnomalyTestResult(TestResult):
    test_metrics: list[AnomalyTestMetric]


class DimensionAnomalyTestMetric(AnomalyTestMetric):
    average: float
    dimension: str
    dimension_value: str


class DimensionAnomalyTestResult(AnomalyTestResult):
    test_metrics: list[DimensionAnomalyTestMetric]


class SourceFreshnessPeriod(BaseModel):
    period: str
    count: int


class SourceFreshnessResult(BaseModel):
    # model_id, max_loaded_at, max_loaded_at_time_ago_in_s, status, warn_after, error_after
    model_id: str
    max_loaded_at: datetime
    status: str
    warn_after: SourceFreshnessPeriod
    error_after: SourceFreshnessPeriod

    @property
    def max_loaded_at_time_ago_in_s(self) -> float:
        return (datetime.utcnow() - self.max_loaded_at).total_seconds()


class SchemaChangeTestResult(BaseModel):
    test_timestamp: datetime
    column_name: str
    test_sub_type: TestSubTypes
    from_type: Optional[str] = None
    to_type: Optional[str] = None

    @property
    def result_description(self) -> dict:
        if self.test_sub_type == TestSubTypes.TYPE_CHANGED:
            return f'The type of "{self.column_name}" was changed from {self.from_type} to {self.to_type}'
        elif self.test_sub_type == TestSubTypes.COLUMN_ADDED:
            return f'The column "{self.column_name}" was added to the schema'
        elif self.test_sub_type == TestSubTypes.COLUMN_REMOVED:
            return f'The column "{self.column_name}" was removed from the schema'
        else:
            return ""


class TestRunResultsInjector(TestsInjector):
    def __init__(self, dbt_runner: DbtRunner) -> None:
        super().__init__(dbt_runner)

    def inject_dbt_test_result(self, test: TestSchema, test_result: DbtTestResult):
        self.dbt_runner.run_operation(
            macro_name="data_injection.inject_elementary_test_result",
            macro_args=dict(
                test_id=test.test_id,
                test_name=test.test_name,
                test_column_name=test.test_column_name,
                test_type=test.test_type.value,
                test_sub_type=test.test_sub_type.value,
                test_params=test.test_params,
                test_timestamp=test_result.test_timestamp.isoformat(),
                test_status=test_result.test_status,
                model_id=test.model_id,
                model_name=test.model_name,
                test_result_rows=[
                    result_row for result_row in test_result.test_result_rows
                ],
                result_description=test_result.result_description,
            ),
        )

    def inject_anomaly_test_result(
        self, test: TestSchema, test_result: AnomalyTestResult
    ):
        self.dbt_runner.run_operation(
            macro_name="data_injection.inject_elementary_test_result",
            macro_args=dict(
                test_id=test.test_id,
                test_name=test.test_name,
                test_column_name=test.test_column_name,
                test_type=test.test_type.value,
                test_sub_type=test.test_sub_type.value,
                test_params=test.test_params,
                test_timestamp=test_result.test_timestamp.isoformat(),
                test_status=test_result.test_status,
                model_id=test.model_id,
                model_name=test.model_name,
                test_result_rows=[metric.dict() for metric in test_result.test_metrics],
                result_description=test_result.result_description,
            ),
        )

    def inject_failed_schema_change_test_result(
        self, test: TestSchema, test_result: SchemaChangeTestResult
    ):
        schema_change_test_result_row = dict(
            database_name="ELEMENTARY_TESTS",
            schema_name="JAFFLE_SHOP",
            table_name=test.model_name,
            column_name=test_result.column_name,
            test_type=TestTypes.SCHEMA_CHANGE.value,
            test_sub_type=test_result.test_sub_type.value,
            test_results_description=test_result.result_description,
        )

        self.dbt_runner.run_operation(
            macro_name="data_injection.inject_elementary_test_result",
            macro_args=dict(
                test_id=test.test_id,
                test_name=test.test_name,
                test_column_name=test_result.column_name,
                test_type=TestTypes.SCHEMA_CHANGE.value,
                test_sub_type=test_result.test_sub_type.value,
                test_params=test.test_params,
                test_timestamp=test_result.test_timestamp.isoformat(),
                test_status="fail",
                model_id=test.model_id,
                model_name=test.model_name,
                test_result_rows=[schema_change_test_result_row],
                result_description=test_result.result_description,
            ),
        )

    def inject_passed_schema_change_test_result(
        self, test: TestSchema, test_timestamp: datetime
    ):
        self.dbt_runner.run_operation(
            macro_name="data_injection.inject_elementary_test_result",
            macro_args=dict(
                test_id=test.test_id,
                test_name=test.test_name,
                test_type=TestTypes.SCHEMA_CHANGE.value,
                test_sub_type=TestSubTypes.GENGERIC.value,
                test_params=test.test_params,
                test_timestamp=test_timestamp.isoformat(),
                test_status="pass",
                model_id=test.model_id,
                model_name=test.model_name,
            ),
        )

    def inject_source_freshness_result(self, test_result: SourceFreshnessResult):
        self.dbt_runner.run_operation(
            macro_name="data_injection.inject_source_freshness_result",
            macro_args=dict(
                model_id=test_result.model_id,
                max_loaded_at=test_result.max_loaded_at.isoformat(),
                max_loaded_at_time_ago_in_s=test_result.max_loaded_at_time_ago_in_s,
                status=test_result.status,
                warn_after=test_result.warn_after.dict(),
                error_after=test_result.error_after.dict(),
            ),
        )

    def delete_test_data(self, test_id: str):
        self.dbt_runner.run_operation(
            "data_injection.delete_test_data", macro_args=dict(test_id=test_id)
        )
