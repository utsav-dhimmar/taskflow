export interface ProjectCreate {
	name: string;
	description?: string | null;
}

export interface ProjectUpdate {
	name?: string | null;
	description?: string | null;
}

export interface ProjectResponse {
	id: string;
	name: string;
	description?: string | null;
	owner_id: string;
	created_at: string;
	updated_at: string;
}
