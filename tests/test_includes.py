def test_docs_for_include_toml_file(run_poe_subproc):
    result = run_poe_subproc(project="includes")
    assert (
        "CONFIGURED TASKS\n"
        "  echo           says what you say\n"
        "  greet          \n"
        "  greet1         \n"
        "  greet2         Issue a greeting from the Iberian Peninsula\n"
    ) in result.capture
    assert result.stdout == ""
    assert result.stderr == ""


def test_run_task_included_from_toml_file(run_poe_subproc):
    result = run_poe_subproc("greet", "Whirl!", project="includes")
    assert result.capture == "Poe => poe_test_echo Hello 'Whirl!'\n"
    assert result.stdout == "Hello Whirl!\n"
    assert result.stderr == ""


def test_run_task_not_included_from_toml_file(run_poe_subproc):
    result = run_poe_subproc("echo", "Whirl!", project="includes")
    assert result.capture == "Poe => poe_test_echo 'Whirl!'\n"
    assert result.stdout == "Whirl!\n"
    assert result.stderr == ""


def test_docs_for_multiple_includes(run_poe_subproc, projects):
    result = run_poe_subproc(
        f'--root={projects["includes/multiple_includes"]}',
    )
    assert (
        "CONFIGURED TASKS\n"
        "  echo                    says what you say\n"
        "  greet                   \n"
        "  greet1                  \n"
        "  greet2                  Issue a greeting from the Iberian Peninsula\n"
        "  reference_peer_include  \n"
        "  laugh                   a mirthful task\n"
    ) in result.capture
    assert result.stdout == ""
    assert result.stderr == ""


def test_running_from_multiple_includes(run_poe_subproc, projects):
    result = run_poe_subproc(
        f'--root={projects["includes/multiple_includes"]}',
        "echo",
        "Whirl!",
        project="includes",
    )
    assert result.capture == "Poe => poe_test_echo 'Whirl!'\n"
    assert result.stdout == "Whirl!\n"
    assert result.stderr == ""

    result = run_poe_subproc(
        f'--root={projects["includes/multiple_includes"]}', "greet", "Whirl!"
    )
    assert result.capture == "Poe => poe_test_echo Hello 'Whirl!'\n"
    assert result.stdout == "Hello Whirl!\n"
    assert result.stderr == ""

    result = run_poe_subproc(
        f'--root={projects["includes/multiple_includes"]}', "laugh"
    )
    assert result.capture == "Poe => poe_test_echo $ONE_LAUGH | tr a-z A-Z\n"
    assert result.stdout == "LOL\n"
    assert result.stderr == ""


def test_reference_peer_include(run_poe_subproc, projects):
    result = run_poe_subproc(
        f'--root={projects["includes/multiple_includes"]}', "reference_peer_include"
    )
    assert (
        result.capture
        == "Poe => poe_test_echo\nPoe => poe_test_echo $ONE_LAUGH | tr a-z A-Z\n"
    )
    assert result.stdout == "\nLOL\n"
    assert result.stderr == ""


def test_docs_for_only_includes(run_poe_subproc, projects):
    result = run_poe_subproc(
        f'--root={projects["includes/only_includes"]}',
    )
    assert (
        "CONFIGURED TASKS\n"
        "  echo           This is ignored becuase it's already defined!\n"  # or not
        "  greet          \n"
        "  greet1         \n"
        "  greet2         Issue a greeting from the Iberian Peninsula\n"
    ) in result.capture
    assert result.stdout == ""
    assert result.stderr == ""


def test_monorepo_contains_only_expected_tasks(run_poe_subproc, projects):
    result = run_poe_subproc(project="monorepo")
    assert result.capture.endswith(
        "CONFIGURED TASKS\n"
        "  get_cwd_0      \n"
        "  get_cwd_1      \n"
        "  add            \n"
        "  get_cwd_2      \n"
        "  subproj3_env   \n"
        "  get_cwd_3      \n"
        "  subproj4_env   \n\n\n"
    )
    assert result.stdout == ""
    assert result.stderr == ""


def test_monorepo_can_also_include_parent(run_poe_subproc, projects, is_windows):
    result = run_poe_subproc(cwd=projects["monorepo/subproject_2"])
    assert result.capture.endswith(
        "CONFIGURED TASKS\n"
        "  add            \n"
        "  get_cwd_2      \n"
        "  extra_task     \n"
        "  get_cwd_0      \n\n\n"
    )
    assert result.stdout == ""
    assert result.stderr == ""

    result = run_poe_subproc("get_cwd_0", cwd=projects["monorepo/subproject_2"])
    assert result.capture == "Poe => import os; print(os.getcwd())\n"
    if is_windows:
        assert result.stdout.endswith(
            "\\tests\\fixtures\\monorepo_project\\subproject_2\n"
        )
    else:
        assert result.stdout.endswith("/tests/fixtures/monorepo_project/subproject_2\n")
    assert result.stderr == ""


def test_set_default_task_type_with_include(run_poe_subproc, projects):
    result = run_poe_subproc("add", cwd=projects["monorepo/subproject_2"])
    assert result.capture == "Poe => 1 + 1\n"
    assert result.stdout == "2\n"
    assert result.stderr == ""


def test_monorepo_runs_each_task_with_expected_cwd(
    run_poe_subproc, projects, is_windows
):
    result = run_poe_subproc("get_cwd_0", project="monorepo")
    assert result.capture == "Poe => import os; print(os.getcwd())\n"
    if is_windows:
        assert result.stdout.endswith("\\tests\\fixtures\\monorepo_project\n")
    else:
        assert result.stdout.endswith("/tests/fixtures/monorepo_project\n")
    assert result.stderr == ""

    result = run_poe_subproc("get_cwd_1", project="monorepo")
    assert result.capture == "Poe => import os; print(os.getcwd())\n"
    if is_windows:
        assert result.stdout.endswith("\\tests\\fixtures\\monorepo_project\n")
    else:
        assert result.stdout.endswith("/tests/fixtures/monorepo_project\n")
    assert result.stderr == ""

    result = run_poe_subproc("get_cwd_2", project="monorepo")
    assert result.capture == "Poe => import os; print(os.getcwd())\n"
    if is_windows:
        assert result.stdout.endswith(
            "\\tests\\fixtures\\monorepo_project\\subproject_2\n"
        )
    else:
        assert result.stdout.endswith("/tests/fixtures/monorepo_project/subproject_2\n")
    assert result.stderr == ""

    result = run_poe_subproc(
        "--root",
        str(projects["monorepo/subproject_3"]),
        "get_cwd_3",
        cwd=projects["example"],
    )
    assert result.capture == "Poe => import os; print(os.getcwd())\n"
    if is_windows:
        assert result.stdout.endswith("\\tests\\fixtures\\example_project\n")
    else:
        assert result.stdout.endswith("/tests/fixtures/example_project\n")
    assert result.stderr == ""


def test_include_subproject_envfiles_no_cwd_set(run_poe_subproc, projects, is_windows):
    result = run_poe_subproc("subproj3_env", project="monorepo")
    assert result.capture == (
        "Poe => echo POE_ROOT:          ${POE_ROOT}\n"
        "echo POE_CWD:           ${POE_CWD}\n"
        "echo POE_CONF_DIR:      ${POE_CONF_DIR}\n"
        "echo POE_ROOT_COPY:     ${POE_ROOT_COPY}\n"
        "echo POE_CWD_COPY:      ${POE_CWD_COPY}\n"
        "echo POE_CONF_DIR_COPY: ${POE_CONF_DIR_COPY}\n"
        "echo REL_ROOT:          ${REL_ROOT}\n"
        "echo REL_PROC_CWD:      ${REL_PROC_CWD}\n"
        "echo REL_SOURCE_CONFIG: ${REL_SOURCE_CONFIG}\n"
        "echo TASK_REL_ROOT:          ${TASK_REL_ROOT}\n"
        "echo TASK_REL_PROC_CWD:      ${TASK_REL_PROC_CWD}\n"
        "echo TASK_REL_SOURCE_CONFIG: ${TASK_REL_SOURCE_CONFIG}\n"
    )
    printed_vars = {
        line.split(": ")[0]: line.split(": ")[1]
        for line in result.stdout.split("\n")
        if ": " in line
    }
    if is_windows:
        assert printed_vars["POE_ROOT"].endswith("\\tests\\fixtures\\monorepo_project")
        assert printed_vars["POE_CWD"].endswith("\\tests\\fixtures\\monorepo_project")
        assert printed_vars["POE_CONF_DIR"].endswith(
            "\\tests\\fixtures\\monorepo_project\\subproject_3"
        )
        assert printed_vars["POE_ROOT_COPY"].endswith(
            "\\tests\\fixtures\\monorepo_project"
        )
        assert printed_vars["POE_CWD_COPY"].endswith(
            "\\tests\\fixtures\\monorepo_project"
        )
        assert printed_vars["POE_CONF_DIR_COPY"].endswith(
            "\\tests\\fixtures\\monorepo_project\\subproject_3"
        )
    else:
        assert printed_vars["POE_ROOT"].endswith("/tests/fixtures/monorepo_project")
        assert printed_vars["POE_CWD"].endswith("/tests/fixtures/monorepo_project")
        assert printed_vars["POE_CONF_DIR"].endswith(
            "/tests/fixtures/monorepo_project/subproject_3"
        )
        assert printed_vars["POE_ROOT_COPY"].endswith(
            "/tests/fixtures/monorepo_project"
        )
        assert printed_vars["POE_CWD_COPY"].endswith("/tests/fixtures/monorepo_project")
        assert printed_vars["POE_CONF_DIR_COPY"].endswith(
            "/tests/fixtures/monorepo_project/subproject_3"
        )
    assert result.stdout.endswith(
        "REL_ROOT: rel to root\n"
        "REL_PROC_CWD: rel to process cwd\n"
        "REL_SOURCE_CONFIG: rel to source config\n"
        "TASK_REL_ROOT: task level rel to root\n"
        "TASK_REL_PROC_CWD: task level rel to process cwd\n"
        "TASK_REL_SOURCE_CONFIG: task level rel to source config\n"
    )
    assert result.stderr == ""


def test_include_subproject_envfiles_with_cwd_set(
    run_poe_subproc, projects, is_windows
):
    result = run_poe_subproc("subproj4_env", project="monorepo")
    assert result.capture == (
        "Poe => echo POE_ROOT:          ${POE_ROOT}\n"
        "echo POE_CWD:           ${POE_CWD}\n"
        "echo POE_CONF_DIR:      ${POE_CONF_DIR}\n"
        "echo POE_ROOT_COPY:     ${POE_ROOT_COPY}\n"
        "echo POE_CWD_COPY:      ${POE_CWD_COPY}\n"
        "echo POE_CONF_DIR_COPY: ${POE_CONF_DIR_COPY}\n"
        "echo FROM_INCLUDE_CWD:  ${FROM_INCLUDE_CWD}\n"
        "echo REL_ROOT:          ${REL_ROOT}\n"
        "echo REL_PROC_CWD:      ${REL_PROC_CWD}\n"
        "echo REL_SOURCE_CONFIG: ${REL_SOURCE_CONFIG}\n"
        "echo TASK_FROM_INCLUDE_CWD:  ${TASK_FROM_INCLUDE_CWD}\n"
        "echo TASK_REL_ROOT:          ${TASK_REL_ROOT}\n"
        "echo TASK_REL_PROC_CWD:      ${TASK_REL_PROC_CWD}\n"
        "echo TASK_REL_SOURCE_CONFIG: ${TASK_REL_SOURCE_CONFIG}\n"
    )
    printed_vars = {
        line.split(": ")[0]: line.split(": ")[1]
        for line in result.stdout.split("\n")
        if ": " in line
    }
    if is_windows:
        assert printed_vars["POE_ROOT"].endswith("\\tests\\fixtures\\monorepo_project")
        assert printed_vars["POE_CWD"].endswith("\\tests\\fixtures\\monorepo_project")
        assert printed_vars["POE_CONF_DIR"].endswith(
            "\\tests\\fixtures\\monorepo_project\\subproject_4\\exec_dir"
        )
        assert printed_vars["POE_ROOT_COPY"].endswith(
            "\\tests\\fixtures\\monorepo_project"
        )
        assert printed_vars["POE_CWD_COPY"].endswith(
            "\\tests\\fixtures\\monorepo_project"
        )
        assert printed_vars["POE_CONF_DIR_COPY"].endswith(
            "\\tests\\fixtures\\monorepo_project\\subproject_4\\exec_dir"
        )
    else:
        assert printed_vars["POE_ROOT"].endswith("/tests/fixtures/monorepo_project")
        assert printed_vars["POE_CWD"].endswith("/tests/fixtures/monorepo_project")
        assert printed_vars["POE_CONF_DIR"].endswith(
            "/tests/fixtures/monorepo_project/subproject_4/exec_dir"
        )
        assert printed_vars["POE_ROOT_COPY"].endswith(
            "/tests/fixtures/monorepo_project"
        )
        assert printed_vars["POE_CWD_COPY"].endswith("/tests/fixtures/monorepo_project")
        assert printed_vars["POE_CONF_DIR_COPY"].endswith(
            "/tests/fixtures/monorepo_project/subproject_4/exec_dir"
        )
    assert result.stdout.endswith(
        "FROM_INCLUDE_CWD: rel to cwd\n"
        "REL_ROOT: rel to root\n"
        "REL_PROC_CWD: rel to process cwd\n"
        "REL_SOURCE_CONFIG: rel to source config\n"
        "TASK_FROM_INCLUDE_CWD: task level rel to cwd\n"
        "TASK_REL_ROOT: task level rel to root\n"
        "TASK_REL_PROC_CWD: task level rel to process cwd\n"
        "TASK_REL_SOURCE_CONFIG: task level rel to source config\n"
    )
    assert result.stderr == ""
