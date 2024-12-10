export class Claim {
  claim_id: string;
  policy_id: string;
  damage_description: string;
  vehicle: string;
  photos?: string[];
  status: string;
  last_updated: string;
}
