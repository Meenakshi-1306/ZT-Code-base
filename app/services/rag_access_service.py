from typing import Any

from sqlalchemy.orm import Session

from app.services.rbac_service import RBACService


class RagAccessService:

    def __init__(self):
        self.rbac_service = RBACService()

    def check_access(
        self,
        db: Session,
        user_id: str,
        organization_id: str,
        resource: str,
        action: str,
        resource_type: str = "resource",
        context: dict[str, Any] | None = None,
    ):
        context = context or {}

        permission_name = f"{resource}:{action}"

        try:
            has_permission = self.rbac_service.user_has_permission(
                db=db,
                user_id=user_id,
                organization_id=organization_id,
                permission_name=permission_name,
            )
        except TypeError:
            # Some existing RBACService implementations
            # use different argument names/signatures.
            has_permission = self._fallback_permission_check(
                db=db,
                user_id=user_id,
                organization_id=organization_id,
                permission_name=permission_name,
            )

        if has_permission:
            risk_score = self._calculate_risk_score(
                access_granted=True,
                context=context,
            )

            risk_level = self._risk_level(risk_score)

            return {
                "access_granted": True,
                "permission": permission_name,
                "risk_level": risk_level,
                "risk_score": risk_score,
                "reason": (
                    f"User has the required permission "
                    f"'{permission_name}'."
                ),
                "recommendation": (
                    "Access can proceed subject to the organization's "
                    "security policies and contextual controls."
                ),
                "context": context,
            }

        risk_score = self._calculate_risk_score(
            access_granted=False,
            context=context,
        )

        risk_level = self._risk_level(risk_score)

        return {
            "access_granted": False,
            "permission": permission_name,
            "risk_level": risk_level,
            "risk_score": risk_score,
            "reason": (
                f"User does not have the required permission "
                f"'{permission_name}'."
            ),
            "recommendation": (
                "Deny the requested access and review the user's "
                "organization role and assigned permissions."
            ),
            "context": context,
        }

    def _fallback_permission_check(
        self,
        db: Session,
        user_id: str,
        organization_id: str,
        permission_name: str,
    ) -> bool:
        """
        Fallback for projects where RBACService exposes a different
        method signature.

        Update this method to exactly match the existing RBACService
        implementation if required.
        """

        try:
            return bool(
                self.rbac_service.user_has_permission(
                    db,
                    user_id,
                    organization_id,
                    permission_name,
                )
            )
        except Exception:
            return False

    def _calculate_risk_score(
        self,
        access_granted: bool,
        context: dict[str, Any],
    ) -> float:

        if not access_granted:
            return 90.0

        score = 20.0

        if context.get("unusual_time"):
            score += 15

        if context.get("untrusted_device"):
            score += 20

        if context.get("unusual_location"):
            score += 15

        if context.get("multiple_failed_logins"):
            score += 20

        if context.get("sensitive_resource"):
            score += 10

        return min(score, 100.0)

    def _risk_level(self, score: float) -> str:

        if score >= 70:
            return "HIGH"

        if score >= 40:
            return "MEDIUM"

        return "LOW"