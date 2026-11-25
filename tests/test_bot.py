
import pytest

from training_data_bot.bot import TrainingDataBot


def test_bot_initializes():
    bot = TrainingDataBot()

    assert bot.loader is not None
    assert bot.documents == {}
    assert bot.datasets == {}
    assert bot.jobs == {}


def test_initial_statistics():
    bot = TrainingDataBot()

    stats = bot.get_statistics()

    assert stats["documents"]["total"] == 0
    assert stats["datasets"]["total"] == 0
    assert stats["jobs"]["total"] == 0


@pytest.mark.asyncio
async def test_bot_cleanup():
    bot = TrainingDataBot()

    await bot.cleanup()


def test_processing_is_not_implemented_yet():
    bot = TrainingDataBot()

    with pytest.raises(NotImplementedError):
        import asyncio
        asyncio.run(bot.process_documents()) 
