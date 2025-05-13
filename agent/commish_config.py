class CommishHomeCheckboxConfig:
    def __init__(self,
        backup_league_files=True,
        retrieve_team_exports_from_server=True,
        retrieve_team_exports_from_your_pc=False,
        break_if_team_files_are_missing=False,
        break_if_trades_are_pending=True,
        demote_release_players_with_dfa_time_left_of_x_days_or_less=False,
        auto_play_days=True,
        create_and_upload_league_file=True,
        create_and_upload_html_reports=True,
        create_sql_dump_for_ms_access=False,
        create_sql_dump_for_mysql=False,
        export_data_to_csv_files=False,
        upload_status_report_to_server=True,
        create_and_send_result_emails=True,
        dfa_days_value=0,
        auto_play_days_value=1
    ):
        self.backup_league_files = backup_league_files
        self.retrieve_team_exports_from_server = retrieve_team_exports_from_server
        self.retrieve_team_exports_from_your_pc = retrieve_team_exports_from_your_pc
        self.break_if_team_files_are_missing = break_if_team_files_are_missing
        self.break_if_trades_are_pending = break_if_trades_are_pending
        self.demote_release_players_with_dfa_time_left_of_x_days_or_less = demote_release_players_with_dfa_time_left_of_x_days_or_less
        self.auto_play_days = auto_play_days
        self.create_and_upload_league_file = create_and_upload_league_file
        self.create_and_upload_html_reports = create_and_upload_html_reports
        self.create_sql_dump_for_ms_access = create_sql_dump_for_ms_access
        self.create_sql_dump_for_mysql = create_sql_dump_for_mysql
        self.export_data_to_csv_files = export_data_to_csv_files
        self.upload_status_report_to_server = upload_status_report_to_server
        self.create_and_send_result_emails = create_and_send_result_emails
        self.dfa_days_value = dfa_days_value
        self.auto_play_days_value = auto_play_days_value 