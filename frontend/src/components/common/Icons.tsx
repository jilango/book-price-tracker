/** Reusable icon components for consistent styling. */

import { IconType } from 'react-icons';
import {
  FaBook,
  FaGem,
  FaDollarSign,
  FaChartBar,
  FaPen,
  FaLink,
  FaChartLine,
  FaCheckCircle,
  FaChartPie,
  FaBell,
} from 'react-icons/fa';

interface IconProps {
  className?: string;
  size?: number;
}

const createIconComponent = (Icon: IconType, defaultSize: number = 24) => {
  return ({ className = '', size = defaultSize }: IconProps) => (
    <Icon className={className} size={size} />
  );
};

export const BookIcon = createIconComponent(FaBook, 24);
export const DiamondIcon = createIconComponent(FaGem, 24);
export const DollarIcon = createIconComponent(FaDollarSign, 24);
export const ChartBarIcon = createIconComponent(FaChartBar, 24);
export const PenIcon = createIconComponent(FaPen, 24);
export const LinkIcon = createIconComponent(FaLink, 24);
export const ChartLineIcon = createIconComponent(FaChartLine, 24);
export const CheckCircleIcon = createIconComponent(FaCheckCircle, 24);
export const ChartPieIcon = createIconComponent(FaChartPie, 24);
export const BellIcon = createIconComponent(FaBell, 24);

