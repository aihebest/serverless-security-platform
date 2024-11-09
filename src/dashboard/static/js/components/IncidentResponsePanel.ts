// src/dashboard/static/js/components/IncidentResponsePanel.ts

interface Incident {
    id: string;
    title: string;
    severity: string;
    status: string;
    createdAt: string;
    affectedResources: string[];
    automatedActions: AutomatedAction[];
}

interface AutomatedAction {
    name: string;
    status: string;
    timestamp: string;
    result?: string;
}

class IncidentResponsePanel {
    private container: HTMLElement;
    private incidents: Map<string, Incident>;

    constructor(containerId: string) {
        this.container = document.getElementById(containerId);
        this.incidents = new Map();
        this.initialize();
    }

    private initialize(): void {
        this.createPanelStructure();
        this.setupEventHandlers();
    }

    private createPanelStructure(): void {
        this.container.innerHTML = `
            <div class="incident-list">
                <h3>Active Incidents</h3>
                <div id="active-incidents"></div>
            </div>
            <div class="incident-details">
                <h3>Incident Details</h3>
                <div id="incident-details-content"></div>
            </div>
            <div class="automated-actions">
                <h3>Automated Actions</h3>
                <div id="automated-actions-list"></div>
            </div>
        `;
    }

    public updateIncident(incident: Incident): void {
        this.incidents.set(incident.id, incident);
        this.refreshIncidentList();
        this.updateIncidentDetails(incident);
    }

    private refreshIncidentList(): void {
        const listContainer = document.getElementById('active-incidents');
        listContainer.innerHTML = '';

        Array.from(this.incidents.values())
            .sort((a, b) => new Date(b.createdAt).getTime() - new Date(a.createdAt).getTime())
            .forEach(incident => {
                const incidentElement = this.createIncidentElement(incident);
                listContainer.appendChild(incidentElement);
            });
    }

    private createIncidentElement(incident: Incident): HTMLElement {
        const element = document.createElement('div');
        element.className = `incident-item severity-${incident.severity.toLowerCase()}`;
        element.innerHTML = `
            <div class="incident-header">
                <span class="incident-title">${incident.title}</span>
                <span class="incident-severity">${incident.severity}</span>
            </div>
            <div class="incident-meta">
                <span class="incident-time">${new Date(incident.createdAt).toLocaleString()}</span>
                <span class="incident-status">${incident.status}</span>
            </div>
        `;

        element.addEventListener('click', () => this.showIncidentDetails(incident));
        return element;
    }

    private showIncidentDetails(incident: Incident): void {
        const detailsContainer = document.getElementById('incident-details-content');
        detailsContainer.innerHTML = `
            <h4>${incident.title}</h4>
            <div class="incident-details-content">
                <p><strong>Status:</strong> ${incident.status}</p>
                <p><strong>Severity:</strong> ${incident.severity}</p>
                <p><strong>Created:</strong> ${new Date(incident.createdAt).toLocaleString()}</p>
                <div class="affected-resources">
                    <h5>Affected Resources</h5>
                    <ul>
                        ${incident.affectedResources.map(resource => `<li>${resource}</li>`).join('')}
                    </ul>
                </div>
            </div>
        `;

        this.updateAutomatedActionsList(incident.automatedActions);
    }

    private updateAutomatedActionsList(actions: AutomatedAction[]): void {
        const actionsContainer = document.getElementById('automated-actions-list');
        actionsContainer.innerHTML = actions.map(action => `
            <div class="action-item status-${action.status.toLowerCase()}">
                <span class="action-name">${action.name}</span>
                <span class="action-status">${action.status}</span>
                <span class="action-time">${new Date(action.timestamp).toLocaleString()}</span>
                ${action.result ? `<div class="action-result">${action.result}</div>` : ''}
            </div>
        `).join('');
    }
}