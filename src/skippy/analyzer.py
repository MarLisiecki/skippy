import os
import re
import gitlab
from const import GITLAB_URL
from utils import load_config_file
import plotly.graph_objects as go


# TODO: Refactor this shitty class 
class SkippyAnalyzer:

    def __init__(self, branch_name: str | None = None) -> None:
        self.token = os.environ.get("GITLAB_TOKEN")
        self.gitlab = gitlab.Gitlab(GITLAB_URL, self.token)
        self.config = load_config_file()
        self.projects = self.get_projects_id()
        self.branch_name = "main" if not branch_name else branch_name

    def get_projects_id(self):
        ids = []
        for repo in self.config["repositories"]:
            ids.append(*list(repo.keys()), )
        return ids

    def get_pipeline_name(self, id: str) -> str:
        for repo in self.config["repositories"]:
            if name := repo.get(id):
                return name

    def parse_pytest_summary(self, pytest_summary: str):
    
        matches = re.findall(r'(\d+) (passed|skipped|failed)', pytest_summary)
        results = {'passed': 0, 'skipped': 0, 'failed': 0}
        for count, status in matches:
            if status in results:
                results[status] = int(count)

        return results
    
    def create_interactive_pie_chart(self, results, id):
    
        fig = go.Figure(data=[go.Pie(labels=list(results.keys()), values=list(results.values()),
                                    marker_colors=['green', 'orange', 'red'], hole=.3)])

        fig.update_layout(title_text="Pytest Summary Results - Pie Chart")
        fig.write_html(f"results/{id}.html")
    
    def analyze(self):
        for project_id in self.projects:
            project = self.gitlab.projects.get(project_id)
            pipelines = project.pipelines.list(ref=self.branch_name, order_by='id', sort='desc')
            found_job = False
            for pipeline in pipelines:
                latest_pipeline = project.pipelines.get(pipeline.id)
                jobs = latest_pipeline.jobs.list(all=True)

                for job in jobs:
                    if job.name == self.get_pipeline_name(project_id):
                        job_details = project.jobs.get(job.id)
                        pytest_traceback = job_details.trace().decode()
                        self.create_interactive_pie_chart(self.parse_pytest_summary(pytest_traceback), project_id)
                        found_job = True
                        break

                if found_job:
                    break

            if not found_job:
                print(f"No job found with the specified name in project {project_id} on branch {self.branch_name}.")


if __name__ == "__main__":
    sa = SkippyAnalyzer()
    sa.analyze()
