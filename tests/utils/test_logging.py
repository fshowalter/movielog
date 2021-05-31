from pytest_mock import MockerFixture

from movielog.utils.logging import logger


def test_formats_headers_with_yellow(mocker: MockerFixture) -> None:
    info_mock = mocker.MagicMock()
    opt_mock = mocker.patch.object(logger.logger, "opt", return_value=info_mock)

    logger.log("==== test header with a {}", "highlighted variable")

    opt_mock.assert_called_with(colors=True, depth=1)

    info_mock.info.assert_called_with(
        "<yellow>====</yellow> test header with a <yellow>{}</yellow>",
        "highlighted variable",
    )


def test_formats_non_header_variables_with_green(mocker: MockerFixture) -> None:
    info_mock = mocker.MagicMock()
    opt_mock = mocker.patch.object(logger.logger, "opt", return_value=info_mock)

    logger.log("test message with a {}", "highlighted variable")

    opt_mock.assert_called_with(colors=True, depth=1)

    info_mock.info.assert_called_with(
        "test message with a <green>{}</green>",
        "highlighted variable",
    )
