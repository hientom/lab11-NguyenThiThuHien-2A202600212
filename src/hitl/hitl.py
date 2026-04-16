"""
Lab 11 — Part 4: Human-in-the-Loop Design
  TODO 12: Confidence Router
  TODO 13: Design 3 HITL decision points
"""
from dataclasses import dataclass


# ============================================================
# TODO 12: Implement ConfidenceRouter
#
# Route agent responses based on confidence scores:
#   - HIGH (>= 0.9): Auto-send to user
#   - MEDIUM (0.7 - 0.9): Queue for human review
#   - LOW (< 0.7): Escalate to human immediately
#
# Special case: if the action is HIGH_RISK (e.g., money transfer,
# account deletion), ALWAYS escalate regardless of confidence.
#
# Implement the route() method.
# ============================================================

HIGH_RISK_ACTIONS = [
    "transfer_money", "delete_account", "send_email",
    "change_password", "update_personal_info"
]


@dataclass
class RoutingDecision:
    """Result of the confidence router."""
    action: str          # "auto_send", "queue_review", "escalate"
    confidence: float
    reason: str
    priority: str        # "low", "normal", "high"
    requires_human: bool
    hitl_model: str      # "Human-on-the-loop", "Human-in-the-loop", "Human-as-tiebreaker"


class ConfidenceRouter:
    """Route agent responses based on confidence and risk level.

    Thresholds:
        HIGH:   confidence >= 0.9 -> auto-send
        MEDIUM: 0.7 <= confidence < 0.9 -> queue for review
        LOW:    confidence < 0.7 -> escalate to human

    High-risk actions always escalate regardless of confidence.
    """

    HIGH_THRESHOLD = 0.9
    MEDIUM_THRESHOLD = 0.7

    def route(self, response: str, confidence: float,
              action_type: str = "general") -> RoutingDecision:
        """Route a response based on confidence score and action type.

        Args:
            response: The agent's response text
            confidence: Confidence score between 0.0 and 1.0
            action_type: Type of action (e.g., "general", "transfer_money")

        Returns:
            RoutingDecision with routing action and metadata
        """
        # 1. Kiểm tra hành động rủi ro cao (Bất kể độ tin cậy bao nhiêu)
        if action_type in HIGH_RISK_ACTIONS:
            action = "escalate"
            hitl_model = "Human-as-tiebreaker"
            priority = "high"
            requires_human = True
            reason = f"High-risk action '{action_type}' requires mandatory human intervention."

        # 2. Độ tin cậy rất cao (Auto-pilot)
        elif confidence >= self.HIGH_THRESHOLD:
            action = "auto_send"
            hitl_model = "Human-on-the-loop"
            priority = "low"
            requires_human = False
            reason = f"High confidence ({confidence:.2f}) meets auto-send threshold."

        # 3. Độ tin cậy trung bình (Cần kiểm duyệt)
        elif confidence >= self.MEDIUM_THRESHOLD:
            action = "queue_review"
            hitl_model = "Human-in-the-loop"
            priority = "normal"
            requires_human = True
            reason = f"Medium confidence ({confidence:.2f}) requires human review."

        # 4. Độ tin cậy thấp (Cần chuyên gia xử lý lại)
        else:
            action = "escalate"
            hitl_model = "Human-as-tiebreaker"
            priority = "high"
            requires_human = True
            reason = f"Low confidence ({confidence:.2f}) is below safety threshold."

        return RoutingDecision(
            action=action,
            confidence=confidence,
            reason=reason,
            priority=priority,
            requires_human=requires_human,
            hitl_model=hitl_model,
        )


# ============================================================
# TODO 13: Design 3 HITL decision points
#
# For each decision point, define:
# - trigger: What condition activates this HITL check?
# - hitl_model: Which model? (human-in-the-loop, human-on-the-loop,
#   human-as-tiebreaker)
# - context_needed: What info does the human reviewer need?
# - example: A concrete scenario
#
# Think about real banking scenarios where human judgment is critical.
# ============================================================

hitl_decision_points = [
    {
        "id": 1,
        "scenario": "Khách hàng yêu cầu chuyển khoản số tiền lớn tới tài khoản mới lần đầu",
        "trigger": "action_type == 'transfer_money' AND amount > 50_000_000 VND AND is_new_beneficiary == True",
        "hitl_model": "Human-in-the-loop",
        "context_for_human": "Lịch sử giao dịch 3 tháng gần nhất, hạn mức ngày của khách hàng, và đánh giá rủi ro từ hệ thống Fraud Detection.",
        "expected_response_time": "< 2 phút",
    },
    {
        "id": 2,
        "scenario": "Yêu cầu thay đổi số điện thoại nhận OTP hoặc địa chỉ email đăng ký",
        "trigger": "action_type == 'update_personal_info' AND sensitive_field == 'phone_number'",
        "hitl_model": "Human-as-tiebreaker",
        "context_for_human": "Ảnh chụp CCCD của khách hàng, ảnh selfie eKYC gần nhất để đối chiếu bằng mắt, và lịch sử đăng nhập thiết bị.",
        "expected_response_time": "< 10 phút",
    },
    {
        "id": 3,
        "scenario": "AI tư vấn các gói vay tín chấp nhưng có độ tự tin thấp về tính chính xác của lãi suất",
        "trigger": "confidence < 0.75 AND intent == 'loan_consultation'",
        "hitl_model": "Human-on-the-loop",
        "context_for_human": "Toàn bộ lịch sử cuộc trò chuyện (Conversation Logs), điểm tín dụng của khách hàng, và bảng biểu phí lãi suất hiện hành.",
        "expected_response_time": "< 5 phút",
    },
]


# ============================================================
# Quick tests
# ============================================================

def test_confidence_router():
    """Test ConfidenceRouter with sample scenarios."""
    router = ConfidenceRouter()

    test_cases = [
        ("Interest rate is 5.5%", 0.95, "general"),
        ("I'll transfer 10M VND", 0.85, "transfer_money"),
        ("Rate is probably around 4-6%", 0.75, "general"),
        ("I'm not sure about this info", 0.5, "general"),
    ]

    print("Testing ConfidenceRouter:")
    print(f"{'Response':<35} {'Conf':<6} {'Action Type':<18} {'Route':<15} {'HITL Model'}")
    print("-" * 110)
    for resp, conf, action in test_cases:
        result = router.route(resp, conf, action)
        print(f"{resp:<35} {conf:<6.2f} {action:<18} {result.action:<15} {result.hitl_model}")


def test_hitl_points():
    """Display HITL decision points."""
    print("\nHITL Decision Points for VinBank:")
    print("=" * 80)
    for dp in hitl_decision_points:
        print(f"\n--- Decision Point #{dp['id']} ---")
        for key, value in dp.items():
            if key != "id":
                # Viết hoa key để dễ đọc hơn
                label = key.replace("_", " ").title()
                print(f"  {label:<25}: {value}")
    print("\n" + "=" * 80)


if __name__ == "__main__":
    test_confidence_router()
    test_hitl_points()
