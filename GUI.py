from PyQt5.QtWidgets import (
    QMainWindow,
    QTabWidget,
    QWidget,
    QVBoxLayout,
    QFrame,
    QHBoxLayout,
    QLabel,
    QGridLayout,
    QGroupBox,
    QScrollArea,
)
from PyQt5.QtCore import QTimer, Qt
from utils.StyleSheet import StyleSheet

from matplotlib.backends.backend_qt5agg import NavigationToolbar2QT
from qt_widgets.BezierTab import BezierTab
from qt_widgets.SectorBoundaryTab import SectorBoundaryTab
from qt_widgets.PathStepsTab import PathStepsTab
from qt_widgets.ControlPanel import ControlPanel
from qt_widgets.Visualizer import Visualizer
from utils.YamlAGVLoader import YamlAGVLoader
from utils.FileDialog import FileDialog
from utils.MapLoader import MapLoader
import time
        

class GUI(QMainWindow):

    def __init__(self) -> None:
        super().__init__()
        self.setWindowTitle("MMRS Simulator")
        # self.setGeometry(100, 100, 1200, 800)
        self.showMaximized()

        self.simulation_start_time = None
        self.simulation_elapsed_time = 0.0
        self.is_simulation_running = False
        
        self.agv_times = {}
        self.numb_of_sect = 0

        self._update_timer = QTimer(self)
        self._update_timer.setInterval(40)
        self._update_timer.timeout.connect(self._on_update_tick)

        self._time_display_timer = QTimer(self)
        self._time_display_timer.setInterval(100)
        self._time_display_timer.timeout.connect(self._update_time_display)

        self._debug_timer = QTimer(self)
        self._debug_timer.setInterval(100)
        self._debug_timer.timeout.connect(self._update_debug_panel)

        self.agv_debug_labels = {}

        central_widget = QFrame()
        central_widget.setStyleSheet(StyleSheet.CentralWidget.value)

        layout = QHBoxLayout(central_widget)

        self.debug_panel = self._create_debug_panel()
        layout.addWidget(self.debug_panel)

        self.tabs = QTabWidget()
        self.tabs.tabBar().setExpanding(True)
        self.tabs.setStyleSheet(StyleSheet.Tab.value)

        self.tab1 = QWidget()
        self.tab2 = QWidget()
        self.tab3 = QWidget()
        self.tab4 = QWidget()
        self.tab5 = QWidget()
        self.tabs.addTab(self.tab1, "Simulation")
        self.tabs.addTab(self.tab2, "Statistics")
        self.tabs.addTab(self.tab3, "Bezier Editor")
        self.tabs.addTab(self.tab4, "Sector Boundary")
        self.tabs.addTab(self.tab5, "Path Steps")

        self.visualizer = Visualizer(self, width=5, height=4, dpi=100)
        self.yaml_agv_loader = YamlAGVLoader()
        self.file_dialog = FileDialog()
        self.map_loader = MapLoader()

        self.agv_time_labels = {}
        self.system_time_label = None

        self._create_tabs_content()

        layout.addWidget(self.tabs, 1)
        self.control_panel = ControlPanel()
        self.control_panel.assign_btn_connect_fns([
            self._on_run_clicked,
            self._on_pause_clicked,
            self._on_reset_clicked,
            self._on_show_paths_clicked,
            self._on_show_mpoints_clicked,
            self._on_show_lines_clicked,
            self._on_show_coll_sect_clicked,
            self._on_show_one_coll_sect_clicked,
            self._on_show_all_clicked,
            self._on_load_pure_agvs_clicked,
            self._on_load_agv_with_map_clicked
        ])
        layout.addWidget(self.control_panel.upper_panel)
        self.setCentralWidget(central_widget)

    def _create_debug_panel(self) -> QFrame:
        panel = QFrame()
        panel.setStyleSheet("background-color: #12121E; border-right: 1px solid #2A2A3A;")
        panel.setFixedWidth(230)

        outer = QVBoxLayout(panel)
        outer.setContentsMargins(8, 8, 8, 8)
        outer.setSpacing(4)

        title = QLabel("AGV Debug")
        title.setStyleSheet("color: #CCCCCC; font-weight: bold; font-size: 13px; background: transparent; border: none;")
        title.setAlignment(Qt.AlignCenter)
        outer.addWidget(title)

        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setStyleSheet("QScrollArea { border: none; background: transparent; } QScrollBar:vertical { width: 6px; }")

        self._debug_content = QWidget()
        self._debug_content.setStyleSheet("background: transparent;")
        self._debug_entries_layout = QVBoxLayout(self._debug_content)
        self._debug_entries_layout.setSpacing(8)
        self._debug_entries_layout.setContentsMargins(0, 0, 0, 0)
        self._debug_entries_layout.addStretch(1)

        scroll.setWidget(self._debug_content)
        outer.addWidget(scroll)
        return panel

    def _init_debug_labels(self) -> None:
        while self._debug_entries_layout.count() > 1:
            item = self._debug_entries_layout.takeAt(0)
            if item and item.widget():
                item.widget().deleteLater()
        self.agv_debug_labels = {}

        for agv in self.visualizer.supervisor.agvs:
            box = QGroupBox(f"AGV {agv.id}")
            box.setStyleSheet(
                f"QGroupBox {{ color: {agv.path_color}; font-weight: bold; font-size: 11px;"
                f" border: 1px solid {agv.path_color}44; border-radius: 4px; margin-top: 10px;"
                f" background: #1A1A2E; }}"
                f"QGroupBox::title {{ subcontrol-origin: margin; left: 6px; padding: 0 2px; }}"
            )
            bl = QGridLayout(box)
            bl.setSpacing(2)
            bl.setContentsMargins(6, 14, 6, 6)

            def row(key_text, grid, r):
                key = QLabel(key_text)
                key.setStyleSheet("color: #666; font-size: 10px; background: transparent;")
                val = QLabel("—")
                val.setStyleSheet("color: #AAAAAA; font-size: 10px; background: transparent;")
                grid.addWidget(key, r, 0)
                grid.addWidget(val, r, 1)
                return val

            status_lbl  = row("status",   bl, 0)
            speed_lbl   = row("speed",    bl, 1)
            target_lbl  = row("target v", bl, 2)
            curve_lbl   = row("curve",    bl, 3)
            t_lbl       = row("t",        bl, 4)
            ph_lbl      = row("PH",       bl, 5)
            r_lbl       = row("R",        bl, 6)

            self._debug_entries_layout.insertWidget(
                self._debug_entries_layout.count() - 1, box
            )
            self.agv_debug_labels[agv.id] = {
                "status": status_lbl, "speed": speed_lbl, "target_v": target_lbl,
                "curve": curve_lbl, "t": t_lbl, "ph": ph_lbl, "r": r_lbl,
            }

        self._debug_timer.start()

    def _update_debug_panel(self) -> None:
        if not hasattr(self, 'visualizer') or not self.visualizer.supervisor:
            return
        status_colors = {"running": "#00AAFF", "iddling": "#FFAA00", "finished": "#00CC44"}
        for agv in self.visualizer.supervisor.agvs:
            lbls = self.agv_debug_labels.get(agv.id)
            if not lbls:
                continue
            st = agv.state.status
            color = status_colors.get(st, "#AAAAAA")
            lbls["status"].setText(st)
            lbls["status"].setStyleSheet(f"color: {color}; font-size: 10px; background: transparent;")
            lbls["speed"].setText(f"{agv.motion_controller.current_velocity:.3f} / {agv.state.max_v} m/s")
            lbls["target_v"].setText(f"{agv.stage_pass.target_v:.3f} m/s")
            lbls["curve"].setText(f"{agv.state.current_curve_idx} / {max(0, len(agv.path)-1)}")
            lbls["t"].setText(f"{agv.state.current_t:.3f}")
            lbls["ph"].setText(str(sorted(agv.state.PH)) if agv.state.PH else "∅")
            lbls["r"].setText(str(sorted(agv.state.R)) if agv.state.R else "∅")

    def _create_tabs_content(self) -> None:
        self._create_simulation_tab()
        self._create_time_stats_tab()
        self._create_bezier_tab()
        self._create_sector_boundary_tab()
        self._create_path_steps_tab()

    def _create_simulation_tab(self) -> None:
        layout1 = QVBoxLayout()
        toolbar = NavigationToolbar2QT(self.visualizer, self.tab1)
        layout1.addWidget(toolbar)
        layout1.addWidget(self.visualizer)
        self.tab1.setLayout(layout1)

    def _create_time_stats_tab(self) -> None:
        layout2 = QVBoxLayout()
        layout2.setContentsMargins(20, 20, 20, 20)
        layout2.setSpacing(15)

        system_group = QGroupBox("System Time")
        system_group.setStyleSheet(StyleSheet.QGroupBoxStatistics.value)
        system_layout = QVBoxLayout(system_group)
        
        self.system_time_label = QLabel("Total time: 0.00 s")
        self.system_time_label.setStyleSheet(StyleSheet.TimeLabel(large=True))
        self.system_time_label.setAlignment(Qt.AlignCenter)
        system_layout.addWidget(self.system_time_label)
        
        self.system_status_label = QLabel("Status: Not started")
        self.system_status_label.setStyleSheet(StyleSheet.StatusLabel.value)
        self.system_status_label.setAlignment(Qt.AlignCenter)
        system_layout.addWidget(self.system_status_label)

        layout2.addWidget(system_group)

        self.robots_group = QGroupBox("Robot Times")
        self.robots_group.setStyleSheet(StyleSheet.QGroupBoxStatistics.value)
        self.robots_layout = QGridLayout(self.robots_group)
        self.robots_layout.setSpacing(10)
        
        headers = ["Robot", "Status", "Time"]
        for col, header in enumerate(headers):
            label = QLabel(header)
            label.setStyleSheet("font-weight: bold; font-size: 14px; color: #CCCCCC;")
            label.setAlignment(Qt.AlignCenter)
            self.robots_layout.addWidget(label, 0, col)

        self.no_robots_label = QLabel("No robots loaded")
        self.no_robots_label.setStyleSheet("color: #888888; font-style: italic;")
        self.no_robots_label.setAlignment(Qt.AlignCenter)
        self.robots_layout.addWidget(self.no_robots_label, 1, 0, 1, 3)

        layout2.addWidget(self.robots_group)
        layout2.addStretch(1)

        self.tab2.setLayout(layout2)

    def _init_robot_time_labels(self) -> None:
        for i in reversed(range(self.robots_layout.count())):
            item = self.robots_layout.itemAt(i)
            if item and item.widget():
                widget = item.widget()
                if widget not in [self.robots_layout.itemAtPosition(0, c).widget() for c in range(3) if self.robots_layout.itemAtPosition(0, c)]:
                    widget.deleteLater()

        self.agv_time_labels = {}
        self.agv_times = {}

        agvs = self.visualizer.supervisor.agvs
        
        if not agvs:
            self.no_robots_label = QLabel("No robots loaded")
            self.no_robots_label.setStyleSheet("color: #888888; font-style: italic;")
            self.no_robots_label.setAlignment(Qt.AlignCenter)
            self.robots_layout.addWidget(self.no_robots_label, 1, 0, 1, 3)
            return

        for row, agv in enumerate(agvs, start=1):
            name_label = QLabel(f"AGV {agv.id}")
            name_label.setStyleSheet(f"color: {agv.path_color}; font-weight: bold; font-size: 14px;")
            name_label.setAlignment(Qt.AlignCenter)
            self.robots_layout.addWidget(name_label, row, 0)

            status_label = QLabel("Waiting")
            status_label.setStyleSheet("color: #AAAAAA; font-size: 14px;")
            status_label.setAlignment(Qt.AlignCenter)
            self.robots_layout.addWidget(status_label, row, 1)

            time_label = QLabel("0.00 s")
            time_label.setStyleSheet("color: #00FF00; font-size: 14px; font-weight: bold;")
            time_label.setAlignment(Qt.AlignCenter)
            self.robots_layout.addWidget(time_label, row, 2)

            self.agv_time_labels[agv.id] = {
                "name": name_label,
                "status": status_label,
                "time": time_label
            }

            self.agv_times[agv.id] = {
                "start": None,
                "end": None,
                "elapsed": 0.0,
                "finished": False
            }

    def _update_time_display(self) -> None:
        if not self.is_simulation_running:
            return

        current_time = time.time()
        
        elapsed = self.simulation_elapsed_time + (current_time - self.simulation_start_time)
        self.system_time_label.setText(f"Total time: {elapsed:.2f} s")

        for agv in self.visualizer.supervisor.agvs:
            agv_id = agv.id
            if agv_id not in self.agv_times:
                continue

            agv_data = self.agv_times[agv_id]
            labels = self.agv_time_labels.get(agv_id)
            
            if not labels:
                continue

            if agv.state.status == "finished" and not agv_data["finished"]:
                agv_data["finished"] = True
                agv_data["end"] = current_time
                agv_data["elapsed"] = agv_data["elapsed"] + (current_time - agv_data["start"]) if agv_data["start"] else 0.0
                labels["status"].setText("Finished")
                labels["status"].setStyleSheet("color: #00FF00; font-size: 14px;")
                labels["time"].setText(f"{agv_data['elapsed']:.2f} s")
                
            elif not agv_data["finished"]:
                if agv_data["start"]:
                    current_elapsed = agv_data["elapsed"] + (current_time - agv_data["start"])
                    labels["time"].setText(f"{current_elapsed:.2f} s")
                
                if agv.state.status == "running":
                    labels["status"].setText("Running")
                    labels["status"].setStyleSheet("color: #00AAFF; font-size: 14px;")
                elif agv.state.status == "iddling":
                    labels["status"].setText("Waiting")
                    labels["status"].setStyleSheet("color: #FFAA00; font-size: 14px;")

        all_finished = all(
            self.agv_times[agv.id]["finished"] 
            for agv in self.visualizer.supervisor.agvs 
            if agv.id in self.agv_times
        )
        
        if all_finished and self.visualizer.supervisor.agvs:
            self._stop_timing()
            self.system_status_label.setText("Status: All robots finished")
            self.system_status_label.setStyleSheet("color: #00FF00; font-size: 14px;")
            self._on_pause_clicked()
            self.control_panel.btn_run.setEnabled(False)
            
        else:
            self.system_status_label.setText("Status: Running")
            self.system_status_label.setStyleSheet("color: #00AAFF; font-size: 14px;")

    def _start_timing(self) -> None:
        current_time = time.time()
        self.simulation_start_time = current_time
        self.is_simulation_running = True
        
        for agv in self.visualizer.supervisor.agvs:
            if agv.id in self.agv_times and not self.agv_times[agv.id]["finished"]:
                if self.agv_times[agv.id]["start"] is None:
                    self.agv_times[agv.id]["start"] = current_time
                else:
                    self.agv_times[agv.id]["start"] = current_time

        self._time_display_timer.start()

    def _stop_timing(self) -> None:
        if not self.is_simulation_running:
            return

        current_time = time.time()
        
        self.simulation_elapsed_time += (current_time - self.simulation_start_time)
        
        for agv in self.visualizer.supervisor.agvs:
            if agv.id in self.agv_times and not self.agv_times[agv.id]["finished"]:
                if self.agv_times[agv.id]["start"]:
                    self.agv_times[agv.id]["elapsed"] += (current_time - self.agv_times[agv.id]["start"])
                    self.agv_times[agv.id]["start"] = None

        self.is_simulation_running = False
        self._time_display_timer.stop()
        
        self.system_status_label.setText("Status: Paused")
        self.system_status_label.setStyleSheet("color: #FFAA00; font-size: 14px;")

    def _reset_timing(self) -> None:
        self.simulation_start_time = None
        self.simulation_elapsed_time = 0.0
        self.is_simulation_running = False
        self._time_display_timer.stop()
        self._debug_timer.start()

        self.system_time_label.setText("Total time: 0.00 s")
        self.system_status_label.setText("Status: Not started")
        self.system_status_label.setStyleSheet(StyleSheet.StatusLabel.value)

        for agv_id, data in self.agv_times.items():
            data["start"] = None
            data["end"] = None
            data["elapsed"] = 0.0
            data["finished"] = False
            
            if agv_id in self.agv_time_labels:
                labels = self.agv_time_labels[agv_id]
                labels["status"].setText("Waiting")
                labels["status"].setStyleSheet("color: #AAAAAA; font-size: 14px;")
                labels["time"].setText("0.00 s")

    def _on_run_clicked(self) -> None:
        self.control_panel.btn_run.setEnabled(False)
        self.control_panel.btn_pause.setEnabled(True)

        self.visualizer.timer.start(50)
        self.visualizer.simulation_f = True
        
        self._start_timing()

    def _on_pause_clicked(self) -> None:
        self.control_panel.btn_run.setEnabled(True)
        self.control_panel.btn_pause.setEnabled(False)

        self.visualizer.timer.stop()
        self.visualizer.simulation_f = False
        
        self._stop_timing()

    def _on_reset_clicked(self) -> None:
        self.control_panel.btn_run.setEnabled(True)
        self.control_panel.btn_pause.setEnabled(False)
        self.visualizer.reset_simulation()
        
        self._reset_timing()

    def _on_show_paths_clicked(self) -> None:
        if self.control_panel.btn_show_paths.isChecked():
            self.control_panel.btn_show_paths.setText("Hide Paths")
            for i in range(self.visualizer.supervisor.get_agvs_number()):
                self.visualizer.draw_curve(i)
        else:
            self.control_panel.btn_show_paths.setText("Show Paths")
            self.visualizer.remove_curves()
        self.visualizer.draw()

    def _on_show_mpoints_clicked(self) -> None:
        if self.control_panel.btn_show_points.isChecked():
            self.control_panel.btn_show_points.setText("Hide Points")
            for i in range(self.visualizer.supervisor.get_agvs_number()):
                self.visualizer.draw_middle_points(i)
        else:
            self.control_panel.btn_show_points.setText("Show Points")
            self.visualizer.remove_middle_points()
        self.visualizer.draw()

    def _on_show_lines_clicked(self) -> None:
        if self.control_panel.btn_show_lines.isChecked():
            self.control_panel.btn_show_lines.setText("Hide Lines")
            for i in range(self.visualizer.supervisor.get_agvs_number()):
                self.visualizer.draw_add_lines(i)
        else:
            self.control_panel.btn_show_lines.setText("Show Lines")
            self.visualizer.remove_lines()
        self.visualizer.draw()

    def _on_show_coll_sect_clicked(self) -> None:
        if self.control_panel.btn_det_col_sec.isChecked():
            self.control_panel.btn_det_col_sec.setText("Hide Coll Sectors")
            self.visualizer.draw_coll_sectors()
        else:
            self.control_panel.btn_det_col_sec.setText("Show Coll Sectors")
            self.visualizer.remove_coll_sectors()
            self.numb_of_sect = 0
        self.visualizer.draw()

    def _on_show_one_coll_sect_clicked(self) -> None:
        self.numb_of_sect += 1
        self.visualizer.draw_next_coll_sector(self.numb_of_sect)
        self.visualizer.draw()

    def _on_show_all_clicked(self) -> None:
        if self.control_panel.btn_show_all.isChecked():
            self.control_panel.btn_show_paths.setCheckable(False)
            self.control_panel.btn_show_points.setCheckable(False)
            self.control_panel.btn_show_lines.setCheckable(False)
            self.control_panel.btn_det_col_sec.setCheckable(False)
            self.control_panel.btn_show_paths.setText("Hide Paths")
            self.control_panel.btn_show_points.setText("Hide Points")
            self.control_panel.btn_show_lines.setText("Hide Lines")
            self.control_panel.btn_det_col_sec.setText("Hide Coll Sectors")
            self.control_panel.btn_show_all.setText("Hide All")
            for i in range(self.visualizer.supervisor.get_agvs_number()):
                self.visualizer.draw_curve(i)
                self.visualizer.draw_middle_points(i)
                self.visualizer.draw_add_lines(i)
                self.visualizer.draw_coll_sectors()
        else:
            self.control_panel.btn_show_paths.setCheckable(True)
            self.control_panel.btn_show_points.setCheckable(True)
            self.control_panel.btn_show_lines.setCheckable(True)
            self.control_panel.btn_det_col_sec.setCheckable(True)
            self.control_panel.btn_show_paths.setText("Show Paths")
            self.control_panel.btn_show_points.setText("Show Points")
            self.control_panel.btn_show_lines.setText("Show Lines")
            self.control_panel.btn_det_col_sec.setText("Show Coll Sectors")
            self.control_panel.btn_show_all.setText("Show All")
            self.visualizer.remove_curves()
            self.visualizer.remove_middle_points()
            self.visualizer.remove_lines()
            self.visualizer.remove_coll_sectors()
            self.numb_of_sect = 0
        self.visualizer.draw()

    def _on_load_agvs_and_map(self, with_map: bool) -> None:

        self.visualizer.reset_visualizer()
        self.visualizer.supervisor.reset_supervisor()

        file_agv = self.file_dialog.get_file("/agvs_desc")
        if file_agv == "": return
        agvs = self.yaml_agv_loader.load_agvs_yaml(file_agv)

        if with_map:
            file_map = self.file_dialog.get_file("/maps")
            if file_map == "": return
            map_data = self.map_loader.load_map(file_map)
            self.visualizer.set_map(map_data)
            self.visualizer.draw_map()

            voronoi_data, distance_field = self.visualizer.generate_voronoi()
            self.visualizer.draw_voronoi()
            self.visualizer.draw_distance_field()

            new_paths = self.visualizer.supervisor.ran_marked_states_gen.generate_multiple_paths(
                num_paths=len(agvs.keys()),
                voronoi_skeleton=voronoi_data,
                distance_field=distance_field
            )

            for i in range(len(agvs.keys())):
                agvs[f"agv{i}"].marked_states = new_paths[i]

        self.visualizer.supervisor.load_agvs(agvs)
        self.visualizer.load_agvs_t()

        self.visualizer.supervisor.trigger_path_creation()
        
        self.visualizer.supervisor.detec_col_sectors()
        self.visualizer.supervisor.merge_agv_sectors()
        self.visualizer.supervisor.global_merge()
        self.visualizer.supervisor.get_all_control_points()

        self.visualizer.draw_marked_states()
        for i in range(self.visualizer.supervisor.get_agvs_number()):
            self.visualizer.draw_agents(i, False)
        self.visualizer.draw()

        self._init_robot_time_labels()
        self._init_debug_labels()
        self._reset_timing()

    def _create_bezier_tab(self) -> None:
        layout = QVBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        self.bezier_editor = BezierTab(self.tab3)
        layout.addWidget(self.bezier_editor)
        self.tab3.setLayout(layout)

    def _create_sector_boundary_tab(self) -> None:
        layout = QVBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        self.sector_boundary_tab = SectorBoundaryTab(self.tab4)
        layout.addWidget(self.sector_boundary_tab)
        self.tab4.setLayout(layout)

    def _create_path_steps_tab(self) -> None:
        layout = QVBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        self.path_steps_tab = PathStepsTab(self.tab5)
        layout.addWidget(self.path_steps_tab)
        self.tab5.setLayout(layout)

    def _on_load_pure_agvs_clicked(self) -> None:
        self._on_load_agvs_and_map(False)

    def _on_load_agv_with_map_clicked(self) -> None:
        self._on_load_agvs_and_map(True)

    def _on_update_tick(self):
        pass

