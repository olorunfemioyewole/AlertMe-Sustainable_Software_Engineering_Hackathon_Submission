from sqlalchemy.ext.asyncio import AsyncSession
from report_service import create_incident_report, get_user_by_phone, INCIDENT_TYPES

# Keyed by sessionId; stores step, incident_type, location_method, phone_number
sessions: dict[str, dict] = {}

_MAIN_MENU = (
    "CON Welcome to SafeAlert\n"
    "1. Report Incident\n"
    "2. Check Area Safety\n"
    "3. Exit"
)

_INCIDENT_MENU = (
    "CON Incident type:\n"
    "1. Armed Robbery\n"
    "2. Kidnapping\n"
    "3. Suspicious Activity\n"
    "4. Vandalism\n"
    "5. Banditry/Terrorism\n"
    "6. Other"
)

_LOCATION_METHOD_MENU = (
    "CON Confirm your location:\n"
    "1. Use registered address\n"
    "2. Enter LGA manually"
)

_ERR_INVALID = "END Invalid input. Please dial in again."
_ERR_DB = "END Something went wrong. Please try again shortly."


def _end_session(session_id: str) -> None:
    sessions.pop(session_id, None)


async def handle_ussd(
    session_id: str, phone_number: str, text: str, db: AsyncSession
) -> str:
    # Africa's Talking sends "" on initial dial; split("*") on "" yields [""]
    parts = text.split("*") if text else []

    # ── Initial dial ─────────────────────────────────────────────────────────
    if not parts:
        sessions[session_id] = {
            "step": "main",
            "phone_number": phone_number,
            "incident_type": None,
            "location_method": None,
        }
        return _MAIN_MENU

    first = parts[0]

    # ── Option 3: Exit ───────────────────────────────────────────────────────
    if first == "3":
        _end_session(session_id)
        return "END Thank you for using SafeAlert. Stay safe."

    # ── Option 1: Report Incident ─────────────────────────────────────────────
    if first == "1":
        # Step 1→2: choose incident type
        if len(parts) == 1:
            sessions.setdefault(session_id, {})["step"] = "incident_type"
            return _INCIDENT_MENU

        incident_option = parts[1]
        if incident_option not in INCIDENT_TYPES:
            _end_session(session_id)
            return _ERR_INVALID

        incident_type = INCIDENT_TYPES[incident_option]

        # Step 2→3: choose location method
        if len(parts) == 2:
            sessions.setdefault(session_id, {}).update(
                {"step": "location_method", "incident_type": incident_type}
            )
            return _LOCATION_METHOD_MENU

        location_choice = parts[2]

        # ── 1 → Use registered address ───────────────────────────────────────
        if location_choice == "1":
            user = await get_user_by_phone(phone_number, db)
            address = (user.registered_address or user.lga) if user else None

            if not address:
                # Fallback: no address on file — ask for manual LGA
                if len(parts) == 3:
                    sessions.setdefault(session_id, {}).update(
                        {"step": "manual_lga_fallback", "incident_type": incident_type}
                    )
                    return "CON No registered address found. Enter your LGA and nearest landmark:"

                # User replied with LGA after the fallback prompt
                # text pattern: 1*{opt}*1*{lga_input}
                lga_input = "*".join(parts[3:])
                try:
                    ref_code = await create_incident_report(
                        session_id=session_id,
                        phone_number=phone_number,
                        incident_type=incident_type,
                        location=lga_input,
                        location_method="manual",
                        db=db,
                    )
                    _end_session(session_id)
                    return f"END Report submitted. Ref: #{ref_code}\nAuthorities notified."
                except Exception:
                    _end_session(session_id)
                    return _ERR_DB

            # Address found — submit immediately (only valid at len==3)
            if len(parts) == 3:
                try:
                    ref_code = await create_incident_report(
                        session_id=session_id,
                        phone_number=phone_number,
                        incident_type=incident_type,
                        location=address,
                        location_method="registered",
                        db=db,
                    )
                    _end_session(session_id)
                    return f"END Report submitted. Ref: #{ref_code}\nAuthorities notified."
                except Exception:
                    _end_session(session_id)
                    return _ERR_DB

        # ── 2 → Enter LGA manually ───────────────────────────────────────────
        elif location_choice == "2":
            if len(parts) == 3:
                sessions.setdefault(session_id, {}).update(
                    {"step": "enter_lga", "location_method": "manual", "incident_type": incident_type}
                )
                return "CON Enter your LGA and nearest landmark:"

            # text pattern: 1*{opt}*2*{lga_input}
            lga_input = "*".join(parts[3:])
            try:
                ref_code = await create_incident_report(
                    session_id=session_id,
                    phone_number=phone_number,
                    incident_type=incident_type,
                    location=lga_input,
                    location_method="manual",
                    db=db,
                )
                _end_session(session_id)
                return f"END Report submitted. Ref: #{ref_code}\nAuthorities notified."
            except Exception:
                _end_session(session_id)
                return _ERR_DB

        _end_session(session_id)
        return _ERR_INVALID

    # ── Option 2: Check Area Safety ───────────────────────────────────────────
    if first == "2":
        if len(parts) == 1:
            sessions.setdefault(session_id, {})["step"] = "area_location"
            return "CON Enter your location and nearest landmark:"

        # text pattern: 2*{location_input}
        location_input = "*".join(parts[1:])
        try:
            ref_code = await create_incident_report(
                session_id=session_id,
                phone_number=phone_number,
                incident_type="Area Safety Check",
                location=location_input,
                location_method="manual",
                db=db,
            )
            _end_session(session_id)
            return f"END Report submitted. Ref: #{ref_code}\nAuthorities notified."
        except Exception:
            _end_session(session_id)
            return _ERR_DB

    _end_session(session_id)
    return _ERR_INVALID
