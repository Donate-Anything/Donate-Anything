import pytest

from donate_anything.charity.tests.factories import (
    AppliedBusinessEdit,
    AppliedBusinessEditFactory,
    AppliedOrganizationEdit,
    AppliedOrganizationEditFactory,
    BusinessApplication,
    BusinessApplicationFactory,
    OrganizationApplication,
    OrganizationApplicationFactory,
    ProposedEdit,
    ProposedEditFactory,
)


@pytest.fixture
def business_application() -> BusinessApplication:
    return BusinessApplicationFactory()


@pytest.fixture
def organization_application() -> OrganizationApplication:
    return OrganizationApplicationFactory()


@pytest.fixture
def organization_application_suggested_edit() -> AppliedOrganizationEdit:
    return AppliedOrganizationEditFactory()


@pytest.fixture
def business_application_suggested_edit() -> AppliedBusinessEdit:
    return AppliedBusinessEditFactory()


@pytest.fixture
def entity_proposed_edit() -> ProposedEdit:
    return ProposedEditFactory()
