from aiogram import Router, F
from aiogram.types import CallbackQuery
from aiogram.utils.keyboard import InlineKeyboardBuilder
from sqlalchemy.orm import Session

from app.infra.db.session import get_session
from app.domain.services.catalog_service import CatalogService, MUSCLE_GROUPS

router = Router(name=__name__)


@router.callback_query(F.data.startswith("prog:level:"))
async def pick_level(call: CallbackQuery) -> None:
	level = call.data.split(":", 2)[2]
	kb = InlineKeyboardBuilder()
	kb.button(text="Сплит", callback_data=f"prog:type:split:{level}")
	kb.button(text="Дом", callback_data=f"prog:type:home:{level}")
	kb.button(text="Улица", callback_data=f"prog:type:street:{level}")
	kb.adjust(3)
	await call.message.edit_text("Выберите тип программы")
	await call.message.edit_reply_markup(reply_markup=kb.as_markup())
	await call.answer()


@router.callback_query(F.data.startswith("prog:type:"))
async def pick_type(call: CallbackQuery) -> None:
	_, _, type_, level = call.data.split(":", 3)
	kb = InlineKeyboardBuilder()
	for mg in MUSCLE_GROUPS:
		text = {
			"back": "Спина",
			"biceps": "Бицепс",
			"triceps": "Трицепс",
			"shoulders": "Плечи",
			"legs": "Ноги",
			"forearms": "Предплечья",
		}[mg]
		kb.button(text=text, callback_data=f"prog:mg:{mg}:{type_}:{level}")
	kb.adjust(2)
	await call.message.edit_text("Выберите группу мышц")
	await call.message.edit_reply_markup(reply_markup=kb.as_markup())
	await call.answer()


@router.callback_query(F.data.startswith("prog:mg:"))
async def show_programs(call: CallbackQuery) -> None:
	_, _, mg, type_, level = call.data.split(":", 4)
	with get_session() as session:  # type: Session
		catalog = CatalogService(session)
		catalog.seed_all()
		views = catalog.list_programs(level=level, type_=type_, muscle_group=mg)
	kb = InlineKeyboardBuilder()
	for pv in views[:10]:
		kb.button(text=pv.program.name, callback_data=f"prog:show:{pv.program.id}")
	kb.adjust(1)
	await call.message.edit_text(f"Программы для {mg} — {level}/{type_}")
	await call.message.edit_reply_markup(reply_markup=kb.as_markup())
	await call.answer()


@router.callback_query(F.data.startswith("prog:show:"))
async def show_program_detail(call: CallbackQuery) -> None:
	program_id = int(call.data.split(":", 2)[2])
	with get_session() as session:  # type: Session
		catalog = CatalogService(session)
		views = catalog.list_programs(level="beginner", type_="split")  # not used, just to ensure seed
		from sqlalchemy import select
		from app.domain.models.program import ProgramExercise, WorkoutProgram
		from app.domain.models.exercise import Exercise
		pe = session.scalars(select(ProgramExercise).where(ProgramExercise.program_id == program_id).order_by(ProgramExercise.order_index)).all()
		ex_ids = [x.exercise_id for x in pe]
		exs = session.scalars(select(Exercise).where(Exercise.id.in_(ex_ids))).all()
		prog = session.get(WorkoutProgram, program_id)
	kb = InlineKeyboardBuilder()
	for ex in exs:
		if ex.video_url:
			kb.button(text=f"Видео: {ex.name}", url=ex.video_url)
	kb.adjust(1)
	desc = f"{prog.name}\nУпражнения:\n" + "\n".join(f"• {ex.name}" for ex in exs)
	await call.message.edit_text(desc)
	await call.message.edit_reply_markup(reply_markup=kb.as_markup())
	await call.answer()