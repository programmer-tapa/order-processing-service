import pytest
from unittest.mock import Mock, AsyncMock
from src.app.infra.events.features.process_events.usecases.USECASE_ProcessEvents import (
    USECASE_ProcessEvents,
)
from src.app.infra.events.features.process_events.schemas.INPUT_ProcessEvents import (
    INPUT_ProcessEvents,
)
from src.app.infra.events.features.process_events.schemas.OUTPUT_ProcessEvents import (
    OUTPUT_ProcessEvents,
)
from src.app.infra.events.entities.event import Event
from src.app.infra.events.entities.abstract_event_processor import (
    AbstractEventProcessor,
)


class TestUSECASE_ProcessEvents:

    @pytest.fixture
    def mock_event(self):
        return Event(id="1", name="TestEvent", data={"key": "value"})

    @pytest.fixture
    def mock_processor(self):
        processor = Mock(spec=AbstractEventProcessor)
        processor.process = AsyncMock(return_value=None)
        return processor

    @pytest.fixture
    def mock_helper(self, mock_processor):
        helper = Mock()
        helper.detect_event_processor = Mock(return_value=mock_processor)
        return helper

    @pytest.fixture
    def usecase(self, mock_helper):
        return USECASE_ProcessEvents(mock_helper)

    @pytest.mark.asyncio
    async def test_execute_success(
        self, usecase, mock_event, mock_helper, mock_processor
    ):
        """Test successful event processing"""
        request = INPUT_ProcessEvents(event=mock_event)

        result = await usecase.execute(request)

        assert result.success is True
        assert "Event processed successfully" in result.message
        assert mock_event.name in result.message
        mock_helper.detect_event_processor.assert_called_once_with(mock_event)
        mock_processor.process.assert_called_once_with(mock_event)

    @pytest.mark.asyncio
    async def test_execute_failure_processor_not_found(self, mock_event):
        """Test failure when event processor cannot be found"""
        mock_helper = Mock()
        mock_helper.detect_event_processor = Mock(
            side_effect=ModuleNotFoundError("No module found")
        )
        usecase = USECASE_ProcessEvents(mock_helper)
        request = INPUT_ProcessEvents(event=mock_event)

        result = await usecase.execute(request)

        assert result.success is False
        assert "Failed to process event" in result.message
        assert "No module found" in result.message

    @pytest.mark.asyncio
    async def test_execute_failure_processor_raises_exception(
        self, usecase, mock_event, mock_processor
    ):
        """Test failure when event processor raises an exception"""
        mock_processor.process = AsyncMock(
            side_effect=RuntimeError("Processing failed")
        )
        request = INPUT_ProcessEvents(event=mock_event)

        result = await usecase.execute(request)

        assert result.success is False
        assert "Failed to process event" in result.message
        assert "Processing failed" in result.message

    @pytest.mark.asyncio
    async def test_execute_returns_output_schema(self, usecase, mock_event):
        """Test that execute returns an OUTPUT_ProcessEvents instance"""
        request = INPUT_ProcessEvents(event=mock_event)

        result = await usecase.execute(request)

        assert isinstance(result, OUTPUT_ProcessEvents)
