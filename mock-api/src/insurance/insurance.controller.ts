import { Controller, Get, Post, Body, Query, HttpCode } from '@nestjs/common';
import { InsuranceService } from './insurance.service';
import { CreateClaimDto } from './dto/create-claim.dto';
import { CalculatePremiumDto } from './dto/calculate-premium.dto';

@Controller('insurance')
export class InsuranceController {
  constructor(private readonly insuranceService: InsuranceService) {}

  @Get('claims')
  findClaim(@Query('claim_id') claimId: string) {
    return this.insuranceService.findClaim(claimId);
  }

  @Post('claims')
  @HttpCode(201)
  createClaim(@Body() createClaimDto: CreateClaimDto) {
    return this.insuranceService.createClaim(createClaimDto);
  }

  @Post('premium')
  calculatePremium(@Body() calculatePremiumDto: CalculatePremiumDto) {
    return this.insuranceService.calculatePremium(calculatePremiumDto);
  }
}
