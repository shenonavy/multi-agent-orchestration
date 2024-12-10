import { Injectable, NotFoundException, UnprocessableEntityException } from '@nestjs/common';
import { CreateClaimDto } from './dto/create-claim.dto';
import { CalculatePremiumDto } from './dto/calculate-premium.dto';
import { Claim } from './entities/claim.entity';

@Injectable()
export class InsuranceService {
  private claims: Claim[] = [];

  findClaim(claimId: string) {
    const claim = this.claims.find(c => c.claim_id === claimId);
    if (!claim) {
      throw new NotFoundException({
        error: 'Claim not found',
        claim_id: claimId
      });
    }
    return claim;
  }

  createClaim(createClaimDto: CreateClaimDto) {
    const claim: Claim = {
      claim_id: Math.random().toString(36).substr(2, 9),
      ...createClaimDto,
      status: 'In Review',
      last_updated: new Date().toISOString().split('T')[0]
    };
    this.claims.push(claim);
    return {
      claim_id: claim.claim_id,
      message: 'Claim submitted successfully.'
    };
  }

  calculatePremium(calculatePremiumDto: CalculatePremiumDto) {
    const { policy_id, current_coverage, new_coverage } = calculatePremiumDto;

    if (new_coverage <= current_coverage) {
      throw new UnprocessableEntityException({
        error: "Invalid coverage amounts. 'new_coverage' must be greater than 'current_coverage'."
      });
    }

    const current_premium = current_coverage * 0.001;
    const new_premium = new_coverage * 0.001;

    return {
      policy_id,
      current_premium,
      new_premium
    };
  }
}
