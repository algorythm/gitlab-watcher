import { config } from "https://deno.land/x/dotenv/mod.ts";

const getIssue = async (id: number): Promise<any> => {
    const issueUrl = url(`/issues/${id}`);
    const issue = await (await fetch(issueUrl, {
        headers: {
            "Private-Token": token
        }
    })).json();

    issue.mr = null;

    if (issue.merge_requests_count > 0) {
        const relatedMrs = await getRelatedMrs(id);
        issue.mr = relatedMrs[0];
    }

    return issue;
}

const getRelatedMrs = async(issueId: number) => {
    const mrUrl = url(`/issues/${issueId}/related_merge_requests`)
    return await (await fetch(mrUrl, {
        headers: {
            "Private-Token": token
        }
    })).json();
}

const getIssueStatus = (issue: any) => {
    let status = 'open';

    if (issue.mr != null && issue.mr.labels.includes('phase::review') && issue.mr.state == 'open') {
        status = 'review'
    } else if (issue.mr != null && issue.mr.labels.includes('phase::in progress') && issue.mr.state == 'open') {
        status = 'in progress'
    } else if (issue.mr != null && issue.mr.state == 'merged') {
        status = 'done'
    } else if (issue.state == 'closed') {
        status = 'cancelled'
    }

    return status;
}

const getStatusForAllIssues = async(issueIds: number[]) => {
    for (const issueId of issueIds) {
        const issue = await getIssue(issueId);
        issue.status = getIssueStatus(issue);

        const mrId = issue.mr ? issue.mr.iid : null;
        console.log(`#${issue.iid} (!${mrId}): ${issue.status}`);
    }
};

const env = config();

const issueIds = [
    673, 645, 642, 640, 679, 650, 654, 657, 659, 660, 661, 663, 664, 665,
    667, 668, 579, 677, 683, 684, 686, 678
];

const token = env.token;
const projectId = env.projectId;

const url = (path: string): string => `${env.base}/api/v4/projects/${projectId}${path}`;

await getStatusForAllIssues(issueIds);
